from enum import Enum


class Strategy(str, Enum):
    FROM_LATEST_TAG = "FROM_LATEST_TAG"
    FROM_DATE = "FROM_DATE"
