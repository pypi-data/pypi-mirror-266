# src/bump440/cli.py
import logging

import typer
from .versions import CurrentVersion, Epoch, Release, Pre, Post, Dev
from .parts import Part
from .logger import get_logger
from .exceptions import InvalidPartError

logger = get_logger(__name__)

app = typer.Typer()


@app.command()
def bump(
    part: Part = typer.Argument(...),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
):
    if verbose:
        logger.setLevel(logging.DEBUG)
    if part == Part.CURRENT:
        print(CurrentVersion().get())
    elif part == Part.EPOCH:
        Epoch().bump()
    elif part == Part.MAJOR:
        Release().bump_major()
    elif part == Part.MINOR:
        Release().bump_minor()
    elif part == Part.MICRO:
        Release().bump_micro()
    elif part == Part.PRE:
        Pre().bump()
    elif part == Part.POST:
        Post().bump()
    elif part == Part.DEV:
        Dev().bump()
    else:
        raise InvalidPartError(
            f"Invalid argument: {part}. Expected one of {list(Part)}."
        )


if __name__ == "__main__":
    app()
