import logging

from alpha.utils.logging_level_checker import logging_level_checker


def test_logging_level_checker():
    # Set logging level to WARNING
    logging.basicConfig(level=logging.WARNING, force=True)

    assert logging_level_checker(level=30, logger_name="root")
    assert logging_level_checker(level="error", logger_name="root")

    assert not logging_level_checker(level=logging.DEBUG, logger_name="root")
    assert not logging_level_checker(level="debug", logger_name="root")

    # Set logging level to DEBUG
    logging.basicConfig(level=logging.DEBUG, force=True)

    assert logging_level_checker(level="debug")
