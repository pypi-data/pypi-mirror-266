from typing import Any

from git_stats_report.utils import run_command


def get_latest_tag() -> str:
    command = "git describe --tags --abbrev=0"
    try:
        return run_command(command)
    except Exception as ex:  # noqa: BLE001
        error_message = "No tags are defined for this repo/branch"
        raise ValueError(error_message) from ex


def get_latest_tag_timestamp(*_: Any) -> Any:
    latest_tag = get_latest_tag()
    command: str = f"git log -1 --format=%aI {latest_tag}"
    return run_command(command)
