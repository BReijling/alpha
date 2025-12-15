import inspect
import logging
import os
from logging import Formatter

import pytest
from alpha.utils.logging_configurator import (
    LoggingConfigurator,
    FORMAT,
    logging_level_checker,
)


@pytest.fixture
def logger_handlers():
    return [
        {
            "type": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "filename": "/tmp/alpha_test_info.log",
            "mode": "w",
        },
        {
            "type": "logging.handlers.TimedRotatingFileHandler",
            "level": "WARNING",
            "filename": "/tmp/alpha_test_warning.log",
            "mode": "w",
        },
        {
            "type": "logging.handlers.WatchedFileHandler",
            "level": "ERROR",
            "filename": "/tmp/alpha_test_error.log",
            "mode": "w",
        },
        {
            "type": "logging.FileHandler",
            "level": "CRITICAL",
            "filename": "/tmp/alpha_test_critical.log",
            "mode": "w",
        },
    ]


@pytest.fixture(autouse=True)
def logger_factory(logger_handlers):
    LoggingConfigurator(handlers=logger_handlers, fmt=None, level=None, stream=None)


@pytest.fixture(autouse=True)
def caplogger(caplog):
    """This is a required fixture to config the caplog fixture."""
    format = Formatter(FORMAT)
    caplog.handler.setFormatter(format)


def test_logging_configurator_stream_handler(caplog):
    debug_msg = "test debug stdout message"
    info_msg = "test info stdout message"

    logging.debug(debug_msg)
    logging.info(info_msg)

    module_name = "test_logging_configurator."
    func_name = inspect.currentframe().f_code.co_name

    assert "DEBUG" not in caplog.text

    assert info_msg in caplog.text
    assert "INFO" in caplog.text
    assert module_name in caplog.text
    assert func_name in caplog.text


def test_logging_configurator_file_handlers():
    info_msg = "test info message"
    warning_msg = "test warning message"
    error_msg = "test error message"
    critical_msg = "test critical message"

    # Creating logs
    logging.info(info_msg)
    logging.warning(warning_msg)
    logging.error(error_msg)
    logging.critical(critical_msg)

    module_name = "test_logging_configurator."
    func_name = inspect.currentframe().f_code.co_name

    info_log_fp = "/tmp/alpha_test_info.log"
    warning_log_fp = "/tmp/alpha_test_warning.log"
    error_log_fp = "/tmp/alpha_test_error.log"
    critical_log_fp = "/tmp/alpha_test_critical.log"

    # Reading all log files
    info_file = open(info_log_fp, "r")
    info_log = info_file.read()
    info_file.close()

    warning_file = open(warning_log_fp, "r")
    warning_log = warning_file.read()
    warning_file.close()

    error_file = open(error_log_fp, "r")
    error_log = error_file.read()
    error_file.close()

    critical_file = open(critical_log_fp, "r")
    critical_log = critical_file.read()
    critical_file.close()

    # Check if the module & funcName are present
    assert module_name in info_log
    assert func_name in info_log

    # Check if all logs are in the right files
    assert info_msg in info_log
    assert warning_msg in info_log
    assert error_msg in info_log
    assert critical_msg in info_log

    assert info_msg not in warning_log
    assert warning_msg in warning_log
    assert error_msg in warning_log
    assert critical_msg in warning_log

    assert info_msg not in error_log
    assert warning_msg not in error_log
    assert error_msg in error_log
    assert critical_msg in error_log

    assert info_msg not in critical_log
    assert warning_msg not in critical_log
    assert error_msg not in critical_log
    assert critical_msg in critical_log

    # Cleaning up
    os.remove(info_log_fp)
    os.remove(warning_log_fp)
    os.remove(error_log_fp)
    os.remove(critical_log_fp)


def test_logging_level_checker():
    assert not logging_level_checker(level="DEBUG")
    assert logging_level_checker(level="INFO")
    assert logging_level_checker(level="WARNING")

    LoggingConfigurator(level="DEBUG")
    assert logging_level_checker(level=10)
