from datetime import datetime, timezone
from secrets import token_hex


def new_id(prefix):
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}_{timestamp}_{token_hex(3)}"
