from __future__ import annotations

import json
from contextlib import suppress
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Union, cast

from typing_extensions import TypedDict

from .utils import levenshtein_distance, run_command

NUM_CHARS = [str(n) for n in range(10)]
LEVENSHTEIN_TRESHOLD = 4


class AuthorStats(TypedDict):
    value: int
    label: str


class GitStatsRawOutput(TypedDict):
    authors: list[AuthorStats]


@dataclass
class AuthorReport:
    author_name: str = ""
    commits: int = 0
    percentage: float = 0.0
    files_changed: int = 0
    lines_added: int = 0
    lines_deleted: int = 0

    def __add__(self: AuthorReport, other: Union[AuthorReport, Any]) -> AuthorReport:  # noqa
        if not isinstance(other, AuthorReport):
            msg = "Addition only works between AuthorReport instances"
            raise TypeError(msg)
        commits = self.commits + other.commits
        percentage = self.percentage + other.percentage
        files_changed = self.files_changed + other.files_changed
        lines_added = self.lines_added + other.lines_added
        lines_deleted = self.lines_deleted + other.lines_deleted
        return AuthorReport(
            author_name=self.author_name,
            commits=commits,
            percentage=percentage,
            files_changed=files_changed,
            lines_added=lines_added,
            lines_deleted=lines_deleted,
        )


def get_git_stats(since: datetime) -> GitStatsRawOutput:
    with suppress(Exception):
        command = f"git-stats --raw --authors --since {since}"
        return cast(GitStatsRawOutput, json.loads(run_command(command)))

    with suppress(Exception):
        command = f"npx git-stats --raw --authors --since {since}"
        return cast(GitStatsRawOutput, json.loads(run_command(command)))

    msg = "Either git-stats or npx (node) must be installed"
    raise ValueError(msg)


def get_total_commits(git_stats: GitStatsRawOutput) -> int:
    return sum(author["value"] for author in git_stats["authors"] if author["value"])


def get_author_info(
    author: AuthorStats, since: datetime, total_commits: int
) -> AuthorReport:
    clean_name: str = format_author_name(author["label"])
    author_name: str = author["label"]
    command: str = (
        f'git log --author="{author_name}" --numstat --since="{since}" --format=""'
    )
    log = run_command(command)
    files_changed = lines_added = lines_deleted = 0
    for line in log.splitlines():
        if not line:
            continue
        added, deleted, _ = line.split("\t", 2)
        files_changed += 1
        lines_added += int(added) if added.isdigit() else 0
        lines_deleted += int(deleted) if deleted.isdigit() else 0
    percentage_of_total = (author["value"] * 100) / total_commits
    return AuthorReport(
        author_name=clean_name,
        commits=int(author["value"]),
        percentage=percentage_of_total,
        files_changed=files_changed,
        lines_added=lines_added,
        lines_deleted=lines_deleted,
    )


def get_reports(
    git_stats: GitStatsRawOutput, since: datetime, total_commits: int
) -> list[AuthorReport]:
    reports: list[AuthorReport] = []

    for author in git_stats["authors"]:
        if not author["value"]:
            continue
        author_report = get_author_info(author, since, total_commits)
        reports.append(author_report)
    return reports


def format_author_name(author: str) -> str:
    name_as_list = author.split(".")
    if "".join(name_as_list).find("-") != -1:
        name_as_list = "".join(name_as_list).split("-")
    formatted_name = " ".join([
        name.capitalize() for name in name_as_list if len(name) > 1
    ])
    if author.find(".") == -1 and author.find("-") == -1:
        formatted_name = author.partition(" (")[0]
    return formatted_name.split("@")[0]


def clean_reports(reports: list[AuthorReport]) -> list[AuthorReport]:
    cleaned_reports: list[AuthorReport] = []

    for outer_index in range(len(reports)):  # pylint: disable=consider-using-enumerate
        if outer_index >= len(reports):  # pylint: disable=consider-using-enumerate
            break
        selected_report: AuthorReport = reports[outer_index]
        for inner_index in range(outer_index + 1, len(reports)):
            if inner_index >= len(reports):
                break
            if (
                levenshtein_distance(
                    selected_report.author_name, reports[inner_index].author_name
                )
                < LEVENSHTEIN_TRESHOLD
            ):
                selected_report += reports[inner_index]
                reports.pop(inner_index)
                inner_index -= 1  # pylint: disable=redefined-loop-name
        cleaned_reports.append(selected_report)
    return cleaned_reports
