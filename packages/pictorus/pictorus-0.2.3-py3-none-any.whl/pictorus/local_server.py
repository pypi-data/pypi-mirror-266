from collections import defaultdict, deque
from queue import Queue
from typing import Dict, Deque, Union, List
from functools import wraps
import json
import http.server
import urllib.parse

from jose import jwt

from .config import Config
from .constants import JWT_ALGORITHM, JWT_PUB_KEY
from .command import CmdType
from .date_utils import utc_timestamp_ms

config = Config()

MAX_RECENT_TELEM_SAMPLES = int(10000)
MAX_TIMESERIES_AGE_S = 300

LocalDbType = Dict[str, Deque[Union[float, List[float], str]]]


class ThreadComms:
    def __init__(self):
        self._data: LocalDbType = defaultdict(lambda: deque(maxlen=MAX_RECENT_TELEM_SAMPLES))
        self.reported_state: Union[dict, None] = None
        self.commands = Queue()

    def add_command(self, cmd_data: dict):
        self.commands.put(cmd_data)

    def update_telem(self, sample: dict):
        for key, val in sample.items():
            if isinstance(val, str):
                try:
                    json_val = json.loads(val)
                    if isinstance(json_val, list):
                        val = json_val
                except json.JSONDecodeError:
                    pass

            self._data[key].append(val)

    def get_telem(
        self, requested_start_time: Union[int, float], max_age_s: Union[int, float]
    ) -> Dict:
        # Copy the current data to lists. This prevents other threads
        # from modifying the data while we're iterating over it.
        data = {key: list(vals) for key, vals in self._data.items()}
        timestamp_data = data.get("utctime")
        if not timestamp_data:
            start_index = 0
        else:
            utc_now = utc_timestamp_ms()
            start_time = max(utc_now - max_age_s * 1000, requested_start_time)
            start_index = next(
                (
                    i
                    for i, ts in enumerate(timestamp_data)
                    if isinstance(ts, float) or isinstance(ts, int) and ts > start_time
                ),
                0,
            )

        return {key: vals[start_index:] for key, vals in data.items()}

    def clear(self):
        self._data.clear()
        self.reported_state = None
        self.commands = Queue()


COMMS = ThreadComms()


class AuthenticationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


def authenticated(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        req = args[0]
        try:
            if "Authorization" not in req.headers:
                raise AuthenticationError("Missing authorization header")

            try:
                token = req.headers["Authorization"].split(" ")[1]
                decoded = jwt.decode(token, JWT_PUB_KEY, algorithms=[JWT_ALGORITHM])
            except Exception as exc:
                raise AuthenticationError("Invalid JWT token") from exc

            if "sub" not in decoded:
                raise AuthenticationError("Missing sub key")

            device_id = decoded["sub"]
            if device_id != config.client_id:
                raise AuthenticationError("Incorrect device ID")
        except AuthenticationError as exc:
            req.send_response(401)
            req.send_header("Content-type", "application/json")
            req.end_headers()
            req.wfile.write(json.dumps({"error": exc.message}).encode())
        else:
            return func(*args, **kwargs)

    return wrapper


class RequestHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "*")
        self.send_header("Allow", "*")
        self.end_headers()

    @authenticated
    def do_GET(self):
        if self.path.startswith("/timeseries"):
            self._handle_timeseries()
        elif self.path.startswith("/devices/"):
            self._handle_get_device()
        else:
            self.send_error(404)

    @authenticated
    def do_POST(self):
        if self.path.startswith("/devices/"):
            self._handle_run_app_route()
        else:
            self.send_error(404)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def _prepare_response(self, response_code=200, data=None):
        self.send_response(response_code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        if data:
            self.wfile.write(json.dumps(data).encode())

    def _handle_timeseries(self):
        query_params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        start_time = float(query_params.get("start_time", [0])[0])
        requested_age_s = int(query_params.get("age_s", [MAX_TIMESERIES_AGE_S])[0])
        max_age_s = min(requested_age_s, MAX_TIMESERIES_AGE_S)
        self._prepare_response(data={"timeseries": COMMS.get_telem(start_time, max_age_s)})

    def _handle_get_device(self):
        device_id = self.path.split("/")[-1]
        self._prepare_response(data={"id": device_id, "reported_state": COMMS.reported_state or {}})

    def _handle_run_app_route(self):
        content_length = int(self.headers.get("Content-Length", 0))
        request_data = json.loads(self.rfile.read(content_length))
        if "run_app" not in request_data or "target" not in request_data:
            self._prepare_response(response_code=400, data={"error": "Missing required fields"})
            return

        cmd_data = {
            "type": CmdType.RUN_APP.value,
            "data": {"run_app": request_data["run_app"]},
            "target": request_data["target"],
        }

        COMMS.add_command(cmd_data)
        self._prepare_response()


def create_server(server_address=("0.0.0.0", 5151), server_class=http.server.HTTPServer):
    return server_class(server_address, RequestHandler)


if __name__ == "__main__":
    server = create_server()
    server.serve_forever()
