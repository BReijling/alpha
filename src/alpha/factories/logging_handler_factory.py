"""Contains LoggerHandlerFactory class"""

from typing import Any

from alpha import exceptions


class LoggingHandlerFactory:
    """For creating a valid logging handler from a dict object.

    Supported handlers:
        - logging.StreamHandler
        - logging.FileHandler
        - logging.handlers.RotatingFileHandler
        - logging.handlers.TimedRotatingFileHandler
        - logging.handlers.WatchedFileHandler
    """

    @classmethod
    def parse(cls, handler: dict[str, Any]) -> dict[str, Any]:
        """Parse a logging handler object.

        Parameters
        ----------
        handler
            A dictionary with at least the 'type' key. All other keys depend on
            the handler type/class. Use the 'logging.handlers' section of the
            python docs to determine which keys can be used for each handler
            type/class.

        Returns
        -------
            A handler dictionary which can be used in the handlers section of a
            logging.config.dictConfig compatible dictionary.

        Raises
        ------
        exceptions.LoggingHandlerException
            - When the 'type' value of the handler is missing or None
            - When a 'FileHandler' is missing the 'filename' value
        """
        type_: str | None = handler.get("type", None)
        if type_ is None:
            raise exceptions.LoggingHandlerException(
                "the logger handler is missing a type attribute"
            )
        *_, class_name = type_.split(".")

        obj: dict[str, Any] = {
            "class": type_,
            "level": handler.get("level", "DEBUG").upper(),
            "formatter": handler.get("formatter", "default"),
        }

        if class_name == "StreamHandler":
            obj.update({"stream": handler.get("stream", "ext://sys.stderr")})
        if "FileHandler" in class_name:
            _filename = handler.get("filename")
            if not _filename:
                raise exceptions.LoggingHandlerException(
                    "the logger handler is missing a filename attribute"
                )
            obj.update(
                {
                    "filename": _filename,
                    "encoding": handler.get("encoding"),
                    "delay": handler.get("delay", False),
                    "errors": handler.get("errors"),
                }
            )
        if "RotatingFileHandler" in class_name:
            obj.update({"backupCount": handler.get("backupCount", 0)})
        if class_name == "RotatingFileHandler":
            obj.update({"maxBytes": handler.get("maxBytes", 0)})
        if class_name == "TimedRotatingFileHandler":
            obj.update(
                {
                    "when": handler.get("when", "h"),
                    "interval": handler.get("interval", 1),
                    "utc": handler.get("utc", False),
                    "atTime": handler.get("atTime"),
                }
            )
        else:
            obj.update({"mode": handler.get("mode", "a")})
        return obj
