import os

import pytest


@pytest.fixture
def path():
    return '/upload-document'


@pytest.fixture
def filename():
    return 'test.txt'


@pytest.fixture
def file(filename):
    this_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(this_path, filename)

    with open(file_path, 'w') as f:
        f.write('test file')
    return file_path


@pytest.fixture
def file_path(file):

    yield file
    # Cleanup after the test
    if os.path.exists(file):
        os.remove(file)


def test_filelist(post, path, file_path, filename, parse_response_json):
    file = file_path
    with open(file, 'rb') as file:
        response = post(path, data={'test_file': file})
    assert response.status_code == 200
    assert parse_response_json(response.data)['data'].endswith(filename)
