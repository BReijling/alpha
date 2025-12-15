"""_summary_
"""
import logging
from logging import getLogger


def logging_level_checker(level: str | int, logger_name: str = "root") -> bool:
    """A simple function to check if a logging level is active.

    Parameters
    ----------
    level : str | int
        The logging level as a string or the corresponding integer
    logger_name : str, optional
        The logger name, by default "root"

    Returns
    -------
    bool
        Returns if the logging level is active
    """
    if isinstance(level, str):
        level_int = getattr(logging, level.upper())
    else:
        level_int = int(level)
    return getLogger(logger_name).level <= level_int
