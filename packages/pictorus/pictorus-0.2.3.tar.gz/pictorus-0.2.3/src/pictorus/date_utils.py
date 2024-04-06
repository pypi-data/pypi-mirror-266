from typing import Union
from datetime import datetime, timezone


def utc_timestamp_ms(dt_utc: Union[datetime, None] = None):
    if dt_utc is None:
        dt_utc = datetime.utcnow()

    return int(round(dt_utc.replace(tzinfo=timezone.utc).timestamp() * 1000))
