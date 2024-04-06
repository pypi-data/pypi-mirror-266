import sys
import time
import subprocess as sp
from threading import Thread
from semver import VersionInfo
from typing import Union

import requests

import pictorus
from pictorus.logging_utils import get_logger
from pictorus.config import Config

logger = get_logger()
config = Config()


class VersionManager:
    """Version manager for pictorus package"""

    # Check for new version every 30 minutes
    CHECK_FREQUENCY_S = 60 * 30
    # If the check fails due to a transient error, try again after 1 minute
    TRANSIENT_FAIL_CHECK_FREQUENCY_S = 60

    def __init__(self):
        self._last_installed: Union[str, None] = None
        self._transient_check_fail = False
        self._run = True
        self._run_thread: Union[Thread, None] = None

    def __enter__(self):
        if not config.auto_update:
            return self

        # Start run_continuously in a separate thread
        self._run = True
        self._run_thread = Thread(target=self._run_continuously)
        self._run_thread.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._run = False
        if self._run_thread:
            self._run_thread.join()

    @property
    def last_installed(self) -> Union[str, None]:
        return self._last_installed

    def check_for_newer_version(self):
        """Check if there is a new version available on pip"""
        try:
            response = requests.get("https://pypi.org/pypi/pictorus/json")
            response.raise_for_status()
        except requests.exceptions.RequestException:
            logger.debug("Could not check if there is a new version of pip available.")
            self._transient_check_fail = True
            return None

        self._transient_check_fail = False

        latest_version = response.json()["info"]["version"]
        latest_version = VersionInfo.parse(latest_version)

        current_version = self._last_installed or pictorus.__version__
        current_version = VersionInfo.parse(current_version)
        if current_version < latest_version:
            return str(latest_version)

        return None

    def install_version(self, version: str):
        """Attempt to install latest version of pictorus package"""
        sp.check_call([sys.executable, "-m", "pip", "install", f"pictorus=={version}"])
        self._last_installed = version

    def _try_update_version(self):
        """Update to the latest version if a newer one is available"""
        new_version = self.check_for_newer_version()
        if not new_version:
            logger.debug("No new version of pictorus is available.")
            return

        logger.info("A new version of pictorus is available. Attempting to update...")
        try:
            self.install_version(new_version)
        except sp.CalledProcessError:
            logger.error("Could not update pictorus. Please update manually.", exc_info=True)
        else:
            logger.info("Update complete. Please restart pictorus to apply.")

    def _run_continuously(self):
        """Run the version manager continuously"""
        next_check_time = 0

        while self._run:
            should_check = time.time() > next_check_time
            if should_check:
                self._try_update_version()

                check_delay = (
                    self.TRANSIENT_FAIL_CHECK_FREQUENCY_S
                    if self._transient_check_fail
                    else self.CHECK_FREQUENCY_S
                )
                next_check_time = time.time() + check_delay
            else:
                time.sleep(1)
