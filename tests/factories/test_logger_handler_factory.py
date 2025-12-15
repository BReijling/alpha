import pytest
from alpha import exceptions
from alpha.factories.logging_handler_factory import LoggingHandlerFactory


def test_stream_handler(stream_handler):
    handler = LoggingHandlerFactory.parse(stream_handler)

    assert handler.get("class") == "logging.StreamHandler"
    assert handler.get("formatter") == "default"
    assert handler.get("level") == "DEBUG"
    assert handler.get("stream") == "ext://sys.stderr"


def test_file_handler(file_handler):
    handler = LoggingHandlerFactory.parse(file_handler)

    assert handler.get("class") == "logging.FileHandler"
    assert handler.get("formatter") == "default"
    assert handler.get("level") == "INFO"
    assert handler.get("filename") == "test.log"
    assert handler.get("mode") == "w"
    assert handler.get("encoding") is None
    assert handler.get("delay") is False
    assert handler.get("errors") is None


def test_file_handler_without_filename(file_handler_without_filename):
    with pytest.raises(exceptions.LoggingHandlerException):
        LoggingHandlerFactory.parse(file_handler_without_filename)


def test_rotating_file_handler(rotating_file_handler):
    handler = LoggingHandlerFactory.parse(rotating_file_handler)

    assert handler.get("class") == "logging.handlers.RotatingFileHandler"
    assert handler.get("formatter") == "default"
    assert handler.get("level") == "WARNING"
    assert handler.get("filename") == "test.log"
    assert handler.get("mode") == "a"
    assert handler.get("encoding") is None
    assert handler.get("delay") is False
    assert handler.get("errors") is None
    assert handler.get("backupCount") == 0
    assert handler.get("maxBytes") == 0


def test_timed_rotating_file_handler(timed_rotating_file_handler):
    handler = LoggingHandlerFactory.parse(timed_rotating_file_handler)

    assert handler.get("class") == "logging.handlers.TimedRotatingFileHandler"
    assert handler.get("formatter") == "default"
    assert handler.get("level") == "ERROR"
    assert handler.get("filename") == "test.log"
    assert handler.get("mode") is None
    assert handler.get("encoding") is None
    assert handler.get("delay") is False
    assert handler.get("errors") is None
    assert handler.get("backupCount") == 0
    assert handler.get("when") == "h"
    assert handler.get("interval") == 1
    assert handler.get("utc") is False
    assert handler.get("atTime") == None


def test_watched_file_handler(watched_file_handler):
    handler = LoggingHandlerFactory.parse(watched_file_handler)

    assert handler.get("class") == "logging.handlers.WatchedFileHandler"
    assert handler.get("formatter") == "default"
    assert handler.get("level") == "CRITICAL"
    assert handler.get("filename") == "test.log"
    assert handler.get("mode") == "a"
    assert handler.get("encoding") is None
    assert handler.get("delay") is False
    assert handler.get("errors") is None
