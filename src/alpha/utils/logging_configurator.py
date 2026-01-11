"""Contains LoggingConfigurator & GunicornLogger classes"""

import logging
from logging.config import dictConfig
from typing import Any

from gunicorn import glogging

from alpha.factories.logging_handler_factory import LoggingHandlerFactory

FORMAT = " | ".join(
    [
        "%(asctime)s",
        "%(name)s",
        "%(levelname)s",
        "%(module)s.%(funcName)s",
        "%(message)s",
    ]
)


class LoggingConfigurator:
    """To create a default logger"""

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        fmt: str = FORMAT,
        handlers: list[dict[str, Any]] | None = None,
        level: str | int = logging.INFO,
        stream: str = "stdout",
        logger_name: str = "root",
    ) -> None:
        """_summary_

        Parameters
        ----------
        config, optional
            _description_, by default None
        fmt, optional
            _description_, by default FORMAT
        handlers, optional
            _description_, by default None
        level, optional
            _description_, by default logging.INFO
        stream, optional
            _description_, by default "stdout"
        logger_name, optional
            _description_, by default 'root'
        """
        if not fmt:
            fmt = FORMAT
        if not stream:
            stream = "stdout"
        if not level:
            level = logging.INFO
        if not handlers:
            handlers = []

        logging_level = (
            getattr(logging, level.upper())
            if isinstance(level, str)
            else level
        )

        default_config: dict[str, Any] = {
            "version": 1,
            "formatters": {"default": {"format": fmt}},
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": logging_level,
                    "formatter": "default",
                    "stream": f"ext://sys.{stream}",
                }
            },
            logger_name: {"level": level, "handlers": ["console"]},
        }

        for ix, handler in enumerate(handlers):
            handler_name = f"handler_{ix}"
            handler_obj = LoggingHandlerFactory.parse(handler)
            default_config["handlers"].update({handler_name: handler_obj})

            default_config[logger_name]["handlers"].append(handler_name)

            handler_level = getattr(logging, handler_obj["level"])
            if handler_level < logging_level:
                logging_level = handler_level
                default_config[logger_name]["level"] = logging_level

        if config:
            dictConfig(config)
        else:
            dictConfig(default_config)


class GunicornLogger(glogging.Logger):
    """This class overrides the default gunicorn logger."""

    def setup(self, cfg: Any):
        """Set the FORMAT on the gunicorn logging handler.

        Args:
            cfg: gunicorn glogging configuration
        """
        super().setup(cfg)  # type: ignore

        self._set_handler(  # type: ignore
            log=self.error_log,
            output=cfg.errorlog,
            fmt=logging.Formatter(fmt=FORMAT),
        )


def logging_level_checker(level: str | int, logger_name: str = "root") -> bool:
    """A simple function to check if a logging level is active.

    Parameters
    ----------
    level : Union[str, int]
        The logging level as a string or the corresponding integer

    Returns
    -------
    bool
        Returns if the logging level is active
    """
    if isinstance(level, str):
        level_int = getattr(logging, level.upper())
    else:
        level_int = level
    return logging.getLogger(logger_name).level <= level_int
