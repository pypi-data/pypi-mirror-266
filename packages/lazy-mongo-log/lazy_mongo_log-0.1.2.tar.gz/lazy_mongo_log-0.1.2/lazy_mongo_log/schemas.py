from datetime import datetime, timezone
from lazy_schema import schema

log_schema = schema(
    message="",
    type="info",
    keyword=None,
    date_created=lambda: datetime.now(timezone.utc),
)
