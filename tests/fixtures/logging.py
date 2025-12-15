import pytest


@pytest.fixture
def stream_handler():
    return {'type': 'logging.StreamHandler'}


@pytest.fixture
def file_handler():
    return {
        'type': 'logging.FileHandler',
        'level': 'info',
        'filename': 'test.log',
        'mode': 'w',
    }


@pytest.fixture
def file_handler_without_filename():
    return {'type': 'logging.FileHandler', 'level': 'info'}


@pytest.fixture
def rotating_file_handler():
    return {
        'type': 'logging.handlers.RotatingFileHandler',
        'level': 'warning',
        'filename': 'test.log',
    }


@pytest.fixture
def timed_rotating_file_handler():
    return {
        'type': 'logging.handlers.TimedRotatingFileHandler',
        'level': 'error',
        'filename': 'test.log',
    }


@pytest.fixture
def watched_file_handler():
    return {
        'type': 'logging.handlers.WatchedFileHandler',
        'level': 'critical',
        'filename': 'test.log',
    }
