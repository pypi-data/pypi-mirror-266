import threading
from unittest import TestCase

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from jose import jwt
import requests

from pictorus.constants import JWT_ALGORITHM
from pictorus.command import CmdType
from pictorus.date_utils import utc_timestamp_ms
from pictorus import local_server
from pictorus.local_server import create_server, COMMS, config

KEY_PAIR = rsa.generate_private_key(public_exponent=65537, key_size=2048)
PUBLIC_KEY = KEY_PAIR.public_key().public_bytes(
    encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
)
PRIVATE_KEY = KEY_PAIR.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption(),
)


class TestLocalServer(TestCase):
    def setUp(self):
        COMMS.clear()

    @classmethod
    def setUpClass(cls):
        local_server.JWT_PUB_KEY = PUBLIC_KEY
        cls._server = create_server(server_address=("localhost", 0))
        cls._base_url = f"http://localhost:{cls._server.server_port}"
        cls._server_thread = threading.Thread(target=cls._server.serve_forever)
        cls._server_thread.start()

    @classmethod
    def tearDownClass(cls):
        if cls._server:
            cls._server.shutdown()

        if cls._server_thread and cls._server_thread.is_alive():
            cls._server_thread.join()

    def test_timeseries(self):
        # Test unauthorized access
        response = requests.get(f"{self._base_url}/timeseries")
        assert response.status_code == 401

        token = jwt.encode({"sub": config.client_id}, PRIVATE_KEY, algorithm=JWT_ALGORITHM)
        headers = {"Authorization": f"Bearer {token}"}

        # Test empty data
        response = requests.get(f"{self._base_url}/timeseries", headers=headers)
        assert response.status_code == 200
        assert response.json() == {"timeseries": {}}

        # Test with data
        utc_now = utc_timestamp_ms()
        ts0 = utc_now
        ts1 = utc_now + 1000
        ts2 = utc_now + 2000
        COMMS.update_telem({"test": 0, "utctime": ts0})
        COMMS.update_telem({"test": 1, "utctime": ts1})
        COMMS.update_telem({"test": 2, "utctime": ts2})
        response = requests.get(f"{self._base_url}/timeseries?start_time={ts0}", headers=headers)
        assert response.status_code == 200
        assert response.json() == {"timeseries": {"test": [1, 2], "utctime": [ts1, ts2]}}

    def test_run_app_route(self):
        # Test unauthorized access
        response = requests.post(f"{self._base_url}/devices/123/run")
        assert response.status_code == 401

        # Test authorized access
        token = jwt.encode({"sub": config.client_id}, PRIVATE_KEY, algorithm=JWT_ALGORITHM)
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        target = {"id": "foo", "type": "process", "options": {}}
        response = requests.post(
            f"{self._base_url}/devices/123/run",
            headers=headers,
            json={"run_app": True, "target": target},
        )
        assert response.status_code == 200
        assert COMMS.commands.get() == {
            "type": CmdType.RUN_APP.value,
            "data": {"run_app": True},
            "target": target,
        }

    def test_get_device(self):
        # Test unauthorized access
        response = requests.get(f"{self._base_url}/devices/123")
        assert response.status_code == 401

        token = jwt.encode({"sub": config.client_id}, PRIVATE_KEY, algorithm=JWT_ALGORITHM)
        headers = {"Authorization": f"Bearer {token}"}
        # Test empty state
        response = requests.get(f"{self._base_url}/devices/123", headers=headers)
        assert response.status_code == 200
        assert response.json() == {"id": "123", "reported_state": {}}

        # Test populated state
        COMMS.reported_state = {"test": 1}
        response = requests.get(f"{self._base_url}/devices/123", headers=headers)
        assert response.status_code == 200
        assert response.json() == {"id": "123", "reported_state": {"test": 1}}

    def test_authenticated_decorator(self):
        # Test missing authorization header
        response = requests.get(self._base_url)
        assert response.status_code == 401

        # Test invalid JWT token
        headers = {"Authorization": "Bearer invalid_token"}
        response = requests.get(self._base_url, headers=headers)
        assert response.status_code == 401

        # Test missing sub key
        token = jwt.encode({}, PRIVATE_KEY, algorithm=JWT_ALGORITHM)
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(self._base_url, headers=headers)
        assert response.status_code == 401

        # Test incorrect device ID
        token = jwt.encode({"sub": "invalid_device_id"}, PRIVATE_KEY, algorithm=JWT_ALGORITHM)
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(self._base_url, headers=headers)
        assert response.status_code == 401

        # Test correct authorization
        token = jwt.encode({"sub": config.client_id}, PRIVATE_KEY, algorithm=JWT_ALGORITHM)
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(self._base_url, headers=headers)
        assert response.status_code == 404
