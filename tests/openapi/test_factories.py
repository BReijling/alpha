from logging import Formatter

import pytest

from alpha.utils.logging_configurator import FORMAT


@pytest.fixture(autouse=True)
def caplogger(caplog):
    """This is a required fixture to config the caplog fixture."""
    format = Formatter(FORMAT)
    caplog.handler.setFormatter(format)


def test_dataclass_factory(post, pet_dict):
    response = post('/dataclass/factory', pet_dict)

    assert response.status_code == 201

    # Check readOnly attributes
    assert response.json['data']['id'] == 1
    assert response.json['data']['age'] == 22


def test_dataclass_default_factory(post, pet_dict):
    response = post('/dataclass/valid', pet_dict)

    assert response.status_code == 201

    # Check readOnly attributes
    assert response.json['data']['id'] == 1
    assert response.json['data']['pet_type'] == 'DOG'
    assert response.json['data']['age'] == 22


def test_dataclass_request_response_factories(post, pet_dict):
    response = post('/dataclass/request_response_factory', pet_dict)

    assert response.status_code == 201

    # Check readOnly attributes
    assert response.json['data']['id'] == 1
    assert response.json['data']['name'] == 'Pluto'

    with pytest.raises(KeyError):
        # attributes not present in MiniPet model
        assert response.json['data']['age']
        assert response.json['data']['pet_type']


def test_dataclass_response_factory_return_list(post, pet_dict):
    response = post('/dataclass/response_factory_list', pet_dict)

    assert response.status_code == 201

    response_data = response.json['data']

    assert isinstance(response_data, list)
    assert len(response_data) == 2

    # Check readOnly attributes
    assert response_data[0]['id'] == 1
    assert response_data[0]['name'] == 'Pluto'
    assert response_data[1]['id'] == 2
    assert response_data[1]['name'] == 'Dug'

    with pytest.raises(KeyError):
        # attributes not present in MiniPet model
        assert response_data[0]['age']
        assert response_data[0]['pet_type']
        assert response_data[1]['age']
        assert response_data[1]['pet_type']


def test_dataclass_factory_age(post, pet_dict):
    response = post(
        '/dataclass/factory', {**pet_dict, 'date_of_birth': '2024-01-01'}
    )
    assert response.status_code == 201

    # Check readOnly attributes
    assert response.json['data']['id'] == 1
    assert response.json['data']['age'] == -2


def test_dataclass_invalid(post, pet_dict):
    # Check if the request fails because the endpoint didn't use
    # `x-alpha-factory` or `x-alpha-request-factory` to map the object
    # to a domain model
    response = post('/dataclass/invalid', pet_dict)
    assert response.status_code == 400


def test_debug_logging(post, pet_dict, caplog):
    post('/dataclass/valid', pet_dict)

    # Check debug logging of the request
    assert (
        'using these parameters: {"pet": {"id": null, "name": "Pluto", '
        in caplog.text
    )
    # Check debug logging of the response when using `x-dsc-debug-response`
    assert (
        'returning response: {"id": 1, "name": "Pluto", "pet_type": "DOG", '
        in caplog.text
    )
