from pyocd.core.helpers import ConnectHelper
from pyocd.flash.file_programmer import FileProgrammer

from .logging_utils import get_logger
from .target_manager import TargetManager
from .command import DeployTarget, Command
from .constants import EMPTY_ERROR

logger = get_logger()


class EmbeddedTargetManager(TargetManager):
    def _deploy_embedded(self, target: DeployTarget):
        self._target_state.error_log = EMPTY_ERROR.copy()
        # This can return None if no targets are found. Need to check this
        # before attempting to use as a ContextManager
        session = ConnectHelper.session_with_chosen_probe(
            blocking=False, return_first=True, target_override=target.options["ocd_target"]
        )
        if not session:
            logger.error("Failed to connect to target")
            self._target_state.error_log = {
                "err_type": "TargetConnectionError",
                "message": "Failed to connect to target. Make sure it is connected and powered on.",
            }
            return

        # Connect to the target
        with session:
            # Create a file programmer and flash the ELF file
            try:
                FileProgrammer(session).program(self._bin_path, file_format="elf")
            except Exception as e:
                logger.error("Failed to flash target", exc_info=True)
                self._target_state.error_log = {
                    "err_type": "TargetFlashError",
                    "message": f"Failed to flash target: {e}",
                }

    def handle_update_app_cmd(self, cmd: Command):
        self._download_app_files(cmd)
        self._deploy_embedded(self._target)

    def handle_set_ttl_cmd(self, cmd: Command):
        pass

    def handle_set_log_level_cmd(self, cmd: Command):
        pass

    def _control_app_running(self, run_app: bool):
        pass

    def open(self):
        pass

    def close(self):
        pass
