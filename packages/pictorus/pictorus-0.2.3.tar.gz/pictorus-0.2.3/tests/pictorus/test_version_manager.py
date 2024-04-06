import sys
from unittest import TestCase, mock
import responses
from subprocess import CalledProcessError

from semver import VersionInfo

import pictorus as pictorus
from pictorus.version_manager import VersionManager


class TestVersionManager(TestCase):
    def setUp(self):
        self.vm = VersionManager()
        self.version = VersionInfo.parse(pictorus.__version__)

    @responses.activate
    def test_check_for_newer_version_has_new_version(self):
        new_version = self.version.bump_minor()
        responses.add(
            responses.GET,
            "https://pypi.org/pypi/pictorus/json",
            json={"info": {"version": str(new_version)}},
        )
        assert self.vm.check_for_newer_version() == str(new_version)

    @responses.activate
    def test_check_for_newer_version_no_update(self):
        responses.add(
            responses.GET,
            "https://pypi.org/pypi/pictorus/json",
            json={"info": {"version": pictorus.__version__}},
        )
        assert self.vm.check_for_newer_version() is None

    @responses.activate
    def test_check_for_newer_version_request_failure(self):
        responses.add(responses.GET, "https://pypi.org/pypi/pictorus/json", status=500)
        assert self.vm.check_for_newer_version() is None
        assert self.vm._transient_check_fail is True

    @responses.activate
    def test_check_for_newer_version_uses_cached_version_from_last_update(self):
        new_version = self.version.bump_minor()
        responses.add(
            responses.GET,
            "https://pypi.org/pypi/pictorus/json",
            json={"info": {"version": str(new_version)}},
        )
        self.vm._last_installed = str(new_version)
        assert self.vm.check_for_newer_version() is None

    @mock.patch("pictorus.version_manager.sp.check_call")
    def test_install_version_success(self, m_check_call):
        version = "1.2.3"
        self.vm.install_version(version)
        m_check_call.assert_called_once_with(
            [sys.executable, "-m", "pip", "install", f"pictorus=={version}"]
        )

    @mock.patch("pictorus.version_manager.sp.check_call")
    def test_install_version_fails(self, m_check_call):
        m_check_call.side_effect = CalledProcessError(99, "pip install")
        version = "2.3.4"
        with self.assertRaises(CalledProcessError):
            self.vm.install_version(version)

        m_check_call.assert_called_once_with(
            [sys.executable, "-m", "pip", "install", f"pictorus=={version}"]
        )
