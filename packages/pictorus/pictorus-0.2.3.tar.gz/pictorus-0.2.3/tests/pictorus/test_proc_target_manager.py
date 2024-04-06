from unittest import TestCase
from unittest.mock import patch, Mock, mock_open
import threading
import json

import responses

from pictorus.constants import AppLogLevel, EMPTY_ERROR
from pictorus.proc_target_manager import ProcTargetManager
from pictorus.command import DeployTarget, Command, CmdType
from pictorus.target_state import TargetState
from ..utils import (
    expected_assets_dir,
    expected_bin_path,
    expected_error_log_path,
    wait_for_condition,
    setup_update_cmd,
)


ADDR_DATA = ("127.0.0.1", 1234)


def _assert_correct_app_start(m_popen, target_id, log_level=AppLogLevel.INFO):
    m_popen.assert_called_once_with(
        expected_bin_path(target_id),
        env={
            "APP_PUBLISH_SOCKET": f"{ADDR_DATA[0]}:{ADDR_DATA[1]}",
            "APP_RUN_PATH": expected_assets_dir(target_id),
            "LOG_LEVEL": log_level.value,
        },
    )


@patch("pictorus.target_manager.os.makedirs", new=Mock())
@patch("pictorus.target_manager.os.chmod", new=Mock())
@patch("pictorus.proc_target_manager._path_exists", return_value=True)
@patch("pictorus.proc_target_manager.Popen")
@patch("pictorus.proc_target_manager.TelemetryManager", return_value=Mock(socket_data=ADDR_DATA))
class TestProcTargetManager(TestCase):
    BUILD_HASH = "abc123"
    TARGET_ID = "foo"
    TARGET = DeployTarget({"id": TARGET_ID, "type": "process"})

    def test_starts_app_on_entry(self, m_telem, m_popen, _):
        target_state = TargetState({"run_app": True, "build_hash": self.BUILD_HASH})
        with ProcTargetManager(self.TARGET, target_state, Mock(), Mock()):
            m_telem.return_value.start_listening.assert_called_once_with(self.BUILD_HASH)
            _assert_correct_app_start(m_popen, self.TARGET_ID)

        m_popen.return_value.terminate.assert_called_once()

    def test_does_not_start_app_on_entry(self, m_telem, m_popen, _):
        target_state = TargetState({"run_app": False, "build_hash": self.BUILD_HASH})
        with ProcTargetManager(self.TARGET, target_state, Mock(), Mock()):
            m_telem.return_value.start_listening.assert_not_called()
            m_popen.assert_not_called()

        m_popen.return_value.terminate.assert_not_called()

    def test_starts_and_stops_app(self, m_telem, m_popen, _):
        target_state = TargetState({"run_app": False, "build_hash": self.BUILD_HASH})
        with ProcTargetManager(self.TARGET, target_state, Mock(), Mock()) as mgr:
            # Start the app
            start_app_cmd = Command(
                {
                    "type": CmdType.RUN_APP.value,
                    "data": {"run_app": True},
                    "target_id": self.TARGET_ID,
                }
            )
            m_telem.reset_mock()
            m_popen.reset_mock()
            mgr.handle_command(start_app_cmd)
            m_telem.return_value.start_listening.assert_called_once_with(self.BUILD_HASH)
            _assert_correct_app_start(m_popen, self.TARGET_ID)

            # Calling start again should do nothing
            m_telem.reset_mock()
            m_popen.reset_mock()
            mgr.handle_command(start_app_cmd)
            m_telem.return_value.start_listening.assert_not_called()
            m_popen.assert_not_called()

            # Stop the app
            stop_app_cmd = Command(
                {
                    "type": CmdType.RUN_APP.value,
                    "data": {"run_app": False},
                    "target_id": self.TARGET_ID,
                }
            )
            m_telem.reset_mock()
            m_popen.reset_mock()
            mgr.handle_command(stop_app_cmd)
            m_telem.return_value.start_listening.assert_not_called()
            m_popen.assert_not_called()
            m_popen.return_value.terminate.assert_called_once()

    @responses.activate
    def test_starts_app_on_update(self, m_telem, m_popen, _):
        new_build_id = "newfoo"
        update_app_cmd, expected_target_state = setup_update_cmd(
            version_url="http://foo.bar/baz",
            params_url="http://foo.bar/params.json",
            build_id=new_build_id,
            params_hash="newparams123",
            target_data=self.TARGET.to_dict(),
        )

        target_state = TargetState({"run_app": True, "build_hash": self.BUILD_HASH})
        with patch("builtins.open"), ProcTargetManager(
            self.TARGET, target_state, Mock(), Mock()
        ) as mgr:
            m_telem.reset_mock()
            m_popen.reset_mock()

            mgr.handle_command(update_app_cmd)
            m_telem.return_value.start_listening.assert_called_once_with(new_build_id)
            _assert_correct_app_start(m_popen, self.TARGET_ID)

            expected_target_state.run_app = True
            assert mgr.target_state_data == expected_target_state.to_dict()

    def test_set_telemetry_ttl(self, m_telem, _, __):
        ttl_s = 99
        set_ttl_cmd = Command(
            {
                "type": CmdType.SET_TELEMETRY_TLL.value,
                "data": {"ttl_s": ttl_s},
                "target_id": self.TARGET_ID,
            }
        )
        target_state = TargetState({"run_app": False, "build_hash": self.BUILD_HASH})
        with ProcTargetManager(self.TARGET, target_state, Mock(), Mock()) as mgr:
            mgr.handle_command(set_ttl_cmd)
            m_telem.return_value.set_ttl.assert_called_once_with(ttl_s)

    def test_set_log_level(self, _, m_popen, __):
        log_level = AppLogLevel.DEBUG
        set_ttl_cmd = Command(
            {
                "type": CmdType.SET_LOG_LEVEL.value,
                "data": {"log_level": log_level.value},
                "target_id": self.TARGET_ID,
            }
        )

        target_state = TargetState({"run_app": True, "build_hash": self.BUILD_HASH})
        with ProcTargetManager(self.TARGET, target_state, Mock(), Mock()) as mgr:
            m_popen.reset_mock()
            mgr.handle_command(set_ttl_cmd)
            _assert_correct_app_start(m_popen, self.TARGET_ID, log_level=log_level)

    @patch("pictorus.proc_target_manager.os.remove")
    def test_sets_error_from_file_on_unexpected_crash(self, m_remove, _, m_popen, __):
        app_complete = threading.Event()
        m_popen.return_value.wait.side_effect = app_complete.wait

        expected_err = {"err_type": "Foo", "message": "Bar"}
        target_state = TargetState({"run_app": True, "build_hash": self.BUILD_HASH})
        m_shadow_cb = Mock()
        with ProcTargetManager(self.TARGET, target_state, Mock(), m_shadow_cb) as mgr, patch(
            "builtins.open", mock_open(read_data=json.dumps(expected_err))
        ):
            # Error should get cleared on init
            wait_for_condition(lambda: m_shadow_cb.call_count == 1)
            assert mgr.target_state_data["error_log"] == EMPTY_ERROR
            app_complete.set()

            # Wait for app to get marked as stopped
            wait_for_condition(lambda: not mgr.app_is_running)

        m_remove.assert_called_once_with(expected_error_log_path(self.TARGET_ID))
        assert m_shadow_cb.call_count == 2
        assert mgr.target_state_data["error_log"] == expected_err

    @patch("pictorus.proc_target_manager.os.remove")
    def test_sets_default_error_on_unexpected_crash(self, m_remove, _, m_popen, m_exists):
        app_complete = threading.Event()
        m_popen.return_value.wait.side_effect = app_complete.wait

        m_exists.side_effect = lambda p: p != expected_error_log_path(self.TARGET_ID)

        target_state = TargetState({"run_app": True, "build_hash": self.BUILD_HASH})
        m_shadow_cb = Mock()
        with ProcTargetManager(self.TARGET, target_state, Mock(), m_shadow_cb) as mgr:
            # Error should get cleared on init
            wait_for_condition(lambda: m_shadow_cb.call_count == 1)
            assert mgr.target_state_data["error_log"] == EMPTY_ERROR
            app_complete.set()

            # Wait for app to get marked as stopped
            wait_for_condition(lambda: not mgr.app_is_running)

        m_remove.assert_not_called()
        assert m_shadow_cb.call_count == 2
        assert mgr.target_state_data["error_log"] == ProcTargetManager.NO_LOG_ERROR
