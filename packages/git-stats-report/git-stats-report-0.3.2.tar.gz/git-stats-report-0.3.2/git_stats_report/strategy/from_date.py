from datetime import datetime, timedelta
from typing import Optional


def days_to_datetime(days_: Optional[str]) -> datetime:
    if not days_:
        error_message = "Days must defined"
        raise ValueError(error_message)

    days = int(days_)

    if days <= 0:
        error_message = f"Days: {days} must be positive"
        raise ValueError(error_message)

    return datetime.now() - timedelta(days=days)
