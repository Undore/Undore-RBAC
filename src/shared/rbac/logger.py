import logging
from typing import Literal

import click
from rich.logging import RichHandler


def init_logger(level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] | None):
    logging.basicConfig(
        level=level,
        format='',
        datefmt="[%X]",
        handlers=[
            RichHandler(rich_tracebacks=True, tracebacks_suppress=[click], omit_repeated_times=False, markup=True)]
    )

    level_to_color = {
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold red"
    }

    class Formatter(logging.Formatter):
        def __init__(self, prefix: str):
            self.prefix = prefix
            self.datefmt = "[%X]"
            self._style = logging.PercentStyle(fmt="")

        def format(self, record):
            levelname = record.levelname
            color = level_to_color.get(levelname, "white")
            formatted = "{prefix}: {message}".format(
                color=color, levelname=levelname, message=record.getMessage(), prefix=self.prefix
            )
            return formatted

    prefix = "[bold magenta]\[RBAC][/bold magenta]"
    handler = RichHandler(rich_tracebacks=True, tracebacks_suppress=[click], omit_repeated_times=False, markup=True)
    handler.setFormatter(Formatter(prefix))

    logger = logging.Logger(prefix, level=level)
    logger.addHandler(handler)
    return logger
