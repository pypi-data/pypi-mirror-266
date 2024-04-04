import logging
from typing import Optional

import typer
from typing_extensions import Annotated

from . import __version__
from .entrypoint import run
from .strategy.strategy import Strategy

app = typer.Typer(add_completion=False)


@app.callback(invoke_without_command=True)
def main(
    strategy: Annotated[
        Strategy,
        typer.Option("--strategy", "-st", help="Get git report since last merge"),
    ] = Strategy.FROM_DATE,
    since_n_days: Annotated[
        Optional[str],
        typer.Option("--since", "-s", help="Get git report since n days"),
    ] = None,
    *,
    raw_format: Annotated[
        bool,
        typer.Option("--raw", "-r", help="Print raw output string with formatting"),
    ] = False,
    version: Annotated[
        bool,
        typer.Option("--version", "-V", help="Shows the version of git-stats-report"),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Print INFO logging statements"),
    ] = False,
    extra_verbose: Annotated[
        bool,
        typer.Option("-vv", help="Print DEBUG logging statements"),
    ] = False,
) -> None:
    """
    Returns a report with all commits authors, amount of commits, percentage of
    total, and also number of files changed, lines added and lines deleted
    """

    if version:
        typer.echo(__version__)
        raise typer.Exit

    if verbose:
        logging.basicConfig(level=logging.INFO)

    if extra_verbose:
        logging.basicConfig(level=logging.DEBUG)

    if since_n_days and strategy is not Strategy.FROM_DATE:
        error_message = "--since is only allowed with --strategy FROM_DATE"
        raise ValueError(error_message)

    run(strategy, since_n_days, raw_format=raw_format)

    raise typer.Exit


if __name__ == "__main__":
    app()
