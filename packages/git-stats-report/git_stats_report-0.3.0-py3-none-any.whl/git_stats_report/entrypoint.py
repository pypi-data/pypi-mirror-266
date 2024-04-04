from typing import List, Optional

from .git_stats import (
    AuthorReport,
    GitStatsRawOutput,
    clean_reports,
    get_git_stats,
    get_reports,
    get_total_commits,
)
from .strategy import Strategy, get_datetime_factory_from_strategy


def run(strategy: Strategy, since: Optional[str], *, raw_format: bool) -> None:
    datetime_factory = get_datetime_factory_from_strategy(strategy)
    since_datetime = datetime_factory(since)

    git_stats: GitStatsRawOutput = get_git_stats(since_datetime)
    total_commits = get_total_commits(git_stats)

    reports: List[AuthorReport] = get_reports(git_stats, since_datetime, total_commits)

    cleaned_reports: List[AuthorReport] = clean_reports(reports)

    output: str = ""

    cleaned_reports.sort(key=lambda report: report.commits, reverse=True)

    for report in cleaned_reports:
        tmp_output = f"{report.author_name}: {report.commits} commits ({report.percentage:.2f}% of total)\n{report.files_changed} Files Changed, - {report.lines_deleted} Lines Deleted, + {report.lines_added} Lines Added\n\n"  # pylint: disable=line-too-long
        if raw_format:
            tmp_output = rf"{report.author_name}: {report.commits} commits ({report.percentage:.2f}% of total)\n{report.files_changed} Files Changed, - {report.lines_deleted} Lines Deleted, + {report.lines_added} Lines Added\n\n"  # pylint: disable=line-too-long
        output += tmp_output
    print(output)
