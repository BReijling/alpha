# Alpha

Alpha is intended to be the first dependency you need to add to your Python application. It is a Python library which contains standard building blocks that can be used in applications that are used as APIs and/or make use of database interaction.

## Badges

[![PyPI version](https://badge.fury.io/py/alpha-python.svg?icon=si%3Apython)](https://badge.fury.io/py/alpha-python)
[![PyPI Downloads](https://img.shields.io/pypi/dm/alpha-python.svg?label=PyPI%20downloads)](https://pypistats.org/packages/alpha-python)
[![Build Status](https://github.com/breijling/alpha/actions/workflows/python-app.yml/badge.svg?branch=main)](https://github.com/breijling/alpha/actions/workflows/python-app.yml)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/alpha-python.svg?color=%2334D058)](https://pypi.org/project/alpha-python)
[![Coverage Status](https://coveralls.io/repos/github/BReijling/alpha/badge.svg?branch=main)](https://coveralls.io/github/BReijling/alpha?branch=main)
[![uv](https://img.shields.io/badge/package%20manager-uv-5C4EE5)](https://docs.astral.sh/uv/)
[![mypy](https://img.shields.io/badge/type%20check-mypy-2A6DB2)](https://mypy-lang.org/)
[![Pytest](https://img.shields.io/badge/testing-pytest-0A9EDC)](https://docs.pytest.org/)
[![PEP8](https://img.shields.io/badge/code%20style-pep8-orange.svg)](https://www.python.org/dev/peps/pep-0008/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Documentation Status](https://readthedocs.org/projects/alpha-python/badge/?version=latest)](https://alpha-python.readthedocs.io/en/latest/)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

## Documentation


Full documentation is available at [alpha-python.readthedocs.io](https://alpha-python.readthedocs.io/).

## Installation

The library is still in development, but you can already install it using pip:

```shell
pip install alpha-python
```

If you want to use the alpha cli for generating API code, you can install it using pip as well:

```shell
pip install alpha-python[api-generator]
```

If you want to add the library to your API project, you can add it to your pyproject.toml file:

```shell
# Poetry example
poetry add alpha-python --extras "flask, postgresql"
poetry add --dev alpha-python --extras "api-generator"

# UV example
uv add alpha-python --extra flask --extra postgresql
uv add --dev alpha-python --extra api-generator
```

## Features

- API code generation
- Authentication and authorization
- Database interaction
- Logging
- Error handling
- And much more!

## Usage

The library contains many components. Below are a few practical examples that map to the guides in the documentation.

### 1) API code generation using OpenAPI spec

```shell
alpha api gen --spec-file specification/openapi.yaml --service-package my_app

alpha api run --port 8080
```

### 2) Authenticate with Keycloak (OIDC)

```python
from alpha import KeyCloakOIDCConnector, KeyCloakProvider

keycloak_connector = KeyCloakOIDCConnector(
	base_url="https://keycloak.example.com",
	realm="myrealm",
	client_id="myclient",
	client_secret="myclientsecret",
)

keycloak_provider = KeyCloakProvider(connector=keycloak_connector)
identity = keycloak_provider.authenticate(username="user1", password="user1_password")
```

### 3) Query data using SqlAlchemyDatabase + SqlAlchemyRepository

```python
from alpha import SqlAlchemyDatabase, SqlAlchemyRepository
from my_app import User

db = SqlAlchemyDatabase(conn_str="postgresql://user:password@localhost:5432/mydatabase")

with db.get_session() as session:
	users = SqlAlchemyRepository[User](session=session, default_model=User)
	user = users.get_by_id(1)
```

### 4) Use Unit of Work for transactional operations

```python
from alpha import (
	RepositoryModel,
	SqlAlchemyDatabase,
	SqlAlchemyRepository,
	SqlAlchemyUnitOfWork,
)
from my_app import User, OrmMapper

db = SqlAlchemyDatabase(..., mapper=OrmMapper)
repositories = [
	RepositoryModel(
		name="users",
		repository=SqlAlchemyRepository[User],
		default_model=User,
	)
]

uow = SqlAlchemyUnitOfWork(db=db, repos=repositories)

with uow:
	user = uow.users.get_by_id(1)
```

See also:

- Design principles and patterns: https://alpha-python.readthedocs.io/en/latest/concepts/design-principles/
- Dependency injection concept: https://alpha-python.readthedocs.io/en/latest/concepts/dependency-injection/
- API code generation guide: https://alpha-python.readthedocs.io/en/latest/guides/api-generation/
- Authentication guide: https://alpha-python.readthedocs.io/en/latest/guides/authentication/
- Database interaction guide: https://alpha-python.readthedocs.io/en/latest/guides/database-interaction/

## Contributing

If you want to contribute to the development of this library, you can fork the repository and create a pull request with your changes.

## License

This library is licensed under the MIT License. See the LICENSE file for more information.
