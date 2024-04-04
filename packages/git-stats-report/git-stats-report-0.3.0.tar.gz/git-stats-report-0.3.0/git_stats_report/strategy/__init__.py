from datetime import datetime
from typing import Callable, Optional

from typing_extensions import assert_never

from .from_date import days_to_datetime
from .from_latest_tag import get_latest_tag_timestamp
from .strategy import Strategy


def get_datetime_factory_from_strategy(
    strategy: Strategy,
) -> Callable[[Optional[str]], datetime]:
    if strategy is Strategy.FROM_DATE:
        return days_to_datetime
    if strategy is Strategy.FROM_LATEST_TAG:
        return get_latest_tag_timestamp

    return assert_never(strategy)


__all__ = ["Strategy", "get_datetime_factory_from_strategy"]
