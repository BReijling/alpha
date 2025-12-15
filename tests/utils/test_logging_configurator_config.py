import logging
from logging import Formatter

import pytest

from alpha.utils.logging_configurator import LoggingConfigurator


@pytest.fixture
def logger_format():
    return "@@@ %(asctime)s | %(levelname)s | %(name)s @@@"


@pytest.fixture
def logger_config(logger_format):
    return {
        "version": 1,
        "formatters": {"default": {"format": logger_format}},
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": "ERROR",
                "stream": "ext://sys.stderr",
            }
        },
        "root": {"handlers": ["console"], "level": "ERROR"},
    }


@pytest.fixture(autouse=True)
def logger_factory(logger_config):
    logger_factory = LoggingConfigurator(config=logger_config)
    return logger_factory


@pytest.fixture(autouse=True)
def caplogger(logger_format, caplog):
    """This is a required fixture to config the caplog fixture."""
    format = Formatter(logger_format)
    caplog.handler.setFormatter(format)


def test_logger_factory_custom_config(caplog):
    warning_msg = "test warning stdout message"
    error_msg = "test error stdout message"

    logging.warning(warning_msg)
    logging.error(error_msg)

    assert "WARNING" not in caplog.text
    assert warning_msg not in caplog.text
    assert error_msg not in caplog.text
    assert "ERROR" in caplog.text
    assert "@@@" in caplog.text
