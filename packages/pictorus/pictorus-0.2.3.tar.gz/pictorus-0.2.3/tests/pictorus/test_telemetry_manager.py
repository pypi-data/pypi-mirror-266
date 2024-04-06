import json
from unittest import TestCase
from unittest.mock import MagicMock, patch, ANY

from awscrt import mqtt

from pictorus.telemetry_manager import TelemetryManager, COMMS
from pictorus.config import Config
from ..utils import wait_for_condition

config = Config()


class TestTelemetryManager(TestCase):
    def setUp(self):
        COMMS.clear()

    def test_set_ttl(self):
        mqtt_connection = MagicMock(spec=mqtt.Connection)
        telemetry_manager = TelemetryManager(mqtt_connection)
        telemetry_manager.set_ttl(60)
        assert telemetry_manager._ttl_dt is not None

    def test_start_stop_listening(self):
        mqtt_connection = MagicMock(spec=mqtt.Connection)
        telemetry_manager = TelemetryManager(mqtt_connection)

        telemetry_manager.start_listening("test_build_id")
        assert telemetry_manager._listener_thread is not None
        assert telemetry_manager._listener_thread.is_alive() is True

        telemetry_manager.stop_listening()
        assert telemetry_manager._listener_thread is None

    @patch("socket.socket")
    def test_listen(self, mock_socket):
        mock_socket_instance = MagicMock()
        sock_data = ("127.0.0.1", 1234)
        mock_socket_instance.getsockname.return_value = sock_data
        mock_socket.return_value.__enter__.return_value = mock_socket_instance

        mqtt_connection = MagicMock(spec=mqtt.Connection)
        telemetry_manager = TelemetryManager(mqtt_connection)
        telemetry_manager.ready.wait(timeout=1)
        telemetry_manager.set_ttl(60)

        # Send some data to the socket
        data = {"foo": 1.0}
        encoded_data = json.dumps(data).encode("utf-8")

        def mock_recv(*args, **kwargs):
            assert telemetry_manager.socket_data == sock_data
            # Hack to stop thread after one loop
            telemetry_manager._listen = False
            return encoded_data

        mock_socket_instance.recv.side_effect = mock_recv

        # Start listening
        build_id = "test_build_id"
        telemetry_manager.start_listening(build_id)
        wait_for_condition(lambda: mqtt_connection.publish.call_count > 0)

        # Check that the data was received and processed
        expected_payload = {"data": data, "time_utc": ANY, "meta": {"build_id": build_id}}
        mqtt_connection.publish.assert_called_once_with(
            topic=f"$aws/rules/app_telemetry_test/dt/pictorus/{config.client_id}/telem",
            payload=ANY,
            qos=mqtt.QoS.AT_LEAST_ONCE,
        )
        actual_payload = json.loads(mqtt_connection.publish.call_args[1]["payload"])
        assert actual_payload == expected_payload

        telem = COMMS.get_telem(0, 60)
        assert telem == {"foo": [1.0], "utctime": [ANY]}
