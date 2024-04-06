from unittest import TestCase
from unittest.mock import patch, Mock

import responses

from pictorus.command import DeployTarget
from pictorus.target_state import TargetState
from pictorus.embedded_target_manager import EmbeddedTargetManager
from ..utils import expected_bin_path, setup_update_cmd


@patch("pictorus.target_manager.os.makedirs", new=Mock())
@patch("pictorus.target_manager.os.chmod", new=Mock())
@patch("pictorus.embedded_target_manager.ConnectHelper.session_with_chosen_probe")
@patch("pictorus.embedded_target_manager.FileProgrammer")
class TestEmbeddedTargetManager(TestCase):
    @responses.activate
    def test_successful_deploy_to_embedded_target(self, m_prog, m_session):
        ocd_target = "stm32f4disco"
        target_id = "foo"
        target_data = {"id": target_id, "type": "embedded", "options": {"ocd_target": ocd_target}}
        update_app_cmd, expected_target_state = setup_update_cmd(
            version_url="http://foo.bar/baz",
            params_url="",
            build_id="newfoo",
            params_hash="",
            target_data=target_data,
        )

        target_mgr = EmbeddedTargetManager(DeployTarget(target_data), TargetState({}))
        with patch("builtins.open"):
            target_mgr.handle_command(update_app_cmd)

        m_session.assert_called_once_with(
            blocking=False, return_first=True, target_override=ocd_target
        )
        m_prog.return_value.program.assert_called_once_with(
            expected_bin_path(target_id), file_format="elf"
        )
        assert target_mgr.target_state_data == expected_target_state.to_dict()

    @responses.activate
    def test_failed_deploy_to_embedded_target_unconnected(self, m_prog, m_session):
        m_session.return_value = None

        ocd_target = "stm32f4disco"
        target_data = {"id": "foo", "type": "embedded", "options": {"ocd_target": ocd_target}}
        update_app_cmd, expected_target_state = setup_update_cmd(
            version_url="http://foo.bar/baz",
            params_url="",
            build_id="newfoo",
            params_hash="",
            target_data=target_data,
        )

        target_mgr = EmbeddedTargetManager(DeployTarget(target_data), TargetState({}))
        with patch("builtins.open"):
            target_mgr.handle_command(update_app_cmd)

        m_session.assert_called_once_with(
            blocking=False, return_first=True, target_override=ocd_target
        )
        m_prog.assert_not_called()

        expected_target_state.error_log = {
            "err_type": "TargetConnectionError",
            "message": "Failed to connect to target. Make sure it is connected and powered on.",
        }
        assert target_mgr.target_state_data == expected_target_state.to_dict()

    @responses.activate
    def test_failed_deploy_to_embedded_target_failed_flash(self, m_prog, m_session):
        m_prog.return_value.program.side_effect = ValueError("foo")

        ocd_target = "stm32f4disco"
        target_id = "foo"
        target_data = {"id": target_id, "type": "embedded", "options": {"ocd_target": ocd_target}}
        update_app_cmd, expected_target_state = setup_update_cmd(
            version_url="http://foo.bar/baz",
            params_url="",
            build_id="newfoo",
            params_hash="",
            target_data=target_data,
        )

        target_mgr = EmbeddedTargetManager(DeployTarget(target_data), TargetState({}))
        with patch("builtins.open"):
            target_mgr.handle_command(update_app_cmd)

        m_session.assert_called_once_with(
            blocking=False, return_first=True, target_override=ocd_target
        )

        m_prog.return_value.program.assert_called_once_with(
            expected_bin_path(target_id), file_format="elf"
        )

        expected_target_state.error_log = {
            "err_type": "TargetFlashError",
            "message": "Failed to flash target: foo",
        }
        assert target_mgr.target_state_data == expected_target_state.to_dict()
