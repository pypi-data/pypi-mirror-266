from subprocess import Popen
import os
import time
import threading
import json
from typing import Callable, Union

from awscrt import mqtt

from .target_state import TargetState
from .config import Config
from .logging_utils import get_logger
from .target_manager import TargetManager
from .telemetry_manager import TelemetryManager
from .command import Command, DeployTarget
from .constants import AppLogLevel, THREAD_SLEEP_TIME_S, EMPTY_ERROR

config = Config()
logger = get_logger()


# Mocking os.path.exists directly on this module causes issues with requests
# So add a wrapper function to mock instead
def _path_exists(path: str) -> bool:
    return os.path.exists(path)


class ProcTargetManager(TargetManager):
    NO_LOG_ERROR = {
        "err_type": "NoLogError",
        "message": "App crashed unexpectedly",
    }

    def __init__(
        self,
        target: DeployTarget,
        target_state: TargetState,
        connection: mqtt.Connection,
        update_shadow_cb: Callable[[], None],
    ):
        super().__init__(target, target_state)
        self._app_log_level = AppLogLevel.INFO
        self._telemetry_manager = TelemetryManager(connection)
        self._pictorus_app_process: Union[Popen, None] = None
        self._error_log_path = os.path.join(self._assets_dir, "pictorus_errors.json")
        self._update_shadow_cb = update_shadow_cb

        self._should_watch_app = True
        self._app_watcher_thread = threading.Thread(target=self._watch_app)
        self._app_watcher_thread.start()

    @property
    def app_is_running(self) -> bool:
        """Return whether the app is currently running"""
        return bool(self._pictorus_app_process)

    def handle_update_app_cmd(self, cmd: Command):
        self._download_app_files(cmd)

        self._target_state.error_log = EMPTY_ERROR.copy()
        self._maybe_start_app()

    def handle_set_ttl_cmd(self, cmd: Command):
        self._telemetry_manager.set_ttl(cmd.data["ttl_s"])

    def handle_set_log_level_cmd(self, cmd: Command):
        log_level = cmd.data["log_level"]
        try:
            log_level = AppLogLevel(log_level)
        except ValueError:
            logger.warning("Received invalid log level: %s", log_level)
            return

        self._app_log_level = log_level
        self._restart_app()

    def _control_app_running(self, run_app: bool):
        if run_app:
            self._maybe_start_app()
        else:
            self._stop_app()

    def open(self):
        self._control_app_running(self._target_state.run_app)

    def close(self):
        self._stop_app()
        self._telemetry_manager.stop_listening()

        self._should_watch_app = False
        if self._app_watcher_thread and self._app_watcher_thread.is_alive():
            self._app_watcher_thread.join()

    def _watch_app(self):
        while self._should_watch_app:
            # If an app process has started, communicate() to catch unexpected terminations.
            if self._pictorus_app_process:
                logger.info("Watching for app crashes")

                # Reset Error shadow state for each new app run
                self._target_state.error_log = EMPTY_ERROR.copy()
                self._update_shadow_cb()

                # Blocks until the app process ends
                self._pictorus_app_process.wait()

                # If app manager knows about shutdown, everything's fine
                if not self.app_is_running:
                    logger.info("Detected normal termination of Pictorus App")
                    continue

                logger.warning("Pictorus App unexpectedly crashed!")
                # Check for PictorusError json file and set the shadow state error log to that.
                if _path_exists(self._error_log_path):
                    logger.warning("Sending Pictorus error logs...")
                    with open(self._error_log_path, "r", encoding="utf-8") as error_file:
                        self._target_state.error_log = json.load(error_file)

                    logger.warning("Error log: %s", self._target_state.error_log)
                    os.remove(self._error_log_path)
                else:
                    # There should always be a log. If not, return a special error so we know.
                    logger.warning("No error logs!")
                    self._target_state.error_log = self.NO_LOG_ERROR.copy()

                # The app has crashed and we've gathered all info, stop the app and push
                # the shadow state
                self._stop_app()
                self._update_shadow_cb()

            # If no app is currently running, prevent tight loop
            time.sleep(THREAD_SLEEP_TIME_S)

        # Exit once self.complete Event() is set
        logger.info("Closing App Watcher thread...")

    def _maybe_start_app(self):
        # Don't start if we're already running or not configured to run
        if not self._target_state.run_app or self._pictorus_app_process:
            logger.debug("Not starting app")
            return

        build_hash = self._target_state.build_hash
        if build_hash and _path_exists(self._bin_path):
            logger.info("Starting pictorus app")
            self._telemetry_manager.start_listening(build_hash)
            # Wait for telemetry manager to be in a good state, but continue if it takes too long
            # so we're able to communicate with device manager even if something goes wrong
            self._telemetry_manager.ready.wait(timeout=30)
            # Could potentially pipe app output back to the backend/user if we want to
            if not self._telemetry_manager.socket_data:
                logger.error(
                    "Unable to bind communication socket for app telemetry. Not starting app."
                )
                return

            host, port = self._telemetry_manager.socket_data
            try:
                self._pictorus_app_process = Popen(
                    self._bin_path,
                    env={
                        "APP_PUBLISH_SOCKET": f"{host}:{port}",
                        "APP_RUN_PATH": self._assets_dir,
                        "LOG_LEVEL": self._app_log_level.value,
                    },
                )
            except OSError:
                logger.error("Failed to start app", exc_info=True)
        else:
            logger.info("No pictorus apps installed")

    def _stop_app(self):
        if self._pictorus_app_process:
            logger.info("Stopping pictorus app")
            app_handle = self._pictorus_app_process
            self._pictorus_app_process = None
            app_handle.terminate()
            app_handle.wait()

    def _restart_app(self):
        self._stop_app()
        self._maybe_start_app()
