# Alpha

**Alpha** is a foundational Python library providing standard building blocks for Python applications that use APIs, authentication and/or database interactions.

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
[![Sponsor](https://img.shields.io/badge/Sponsor-GitHub-pink?logo=github)](https://github.com/sponsors/BReijling)

## TL;DR

Alpha provides a comprehensive set of tools for building Python applications that interact with APIs and databases, including API code generation, authentication and authorization, database access layers, error handling, logging, and more. It is designed to be the first dependency you add to your project, providing a solid foundation for your application's architecture.

## Core features

- **API code generation** — OpenAPI code generation via CLI, Flask integration, request/response utilities
- **Authentication & Authorization** — OIDC/KeyCloak, LDAP/Active Directory, JWT and password-based authentication
- **Database access layer** — SQLAlchemy abstraction with Repository and Unit of Work patterns
- **REST API access layer** — REST API repository implementations for external API interactions
- **Model support** — Domain models with audit trail, attrs, Pydantic, dataclasses and OpenAPI model support
- **Error handling** — Custom exceptions, error handlers and standardized error responses
- **Logging** — Structured logging with context support, log enrichment and integration with logging frameworks
- **JSON Serialization** — `JSONEncoder` for complex types: numpy, pandas, datetime, UUID, Enums and dataclasses

## Installation

Install the core library:

```shell
pip install alpha-python
```

Install with optional extras:

```shell
# Flask APIs with PostgreSQL
pip install alpha-python[flask,postgresql]

# CLI for OpenAPI code generation (development dependency)
pip install alpha-python[api-generator]
```

See [Installation](installation.md) for all available extras and package manager examples (Poetry, uv).

## Quick example

```python
from alpha import SqlAlchemyDatabase, SqlAlchemyUnitOfWork, SqlAlchemyRepository

# Configure database
db = SqlAlchemyDatabase("postgresql+psycopg2://user:pass@localhost/mydb")

# Use the Unit of Work pattern
with SqlAlchemyUnitOfWork(db) as uow:
    user = uow.users.get_by_id(1)
```

## Learn more

<div class="grid cards" markdown>

-   :material-download: **Installation**

    ---

    All available extras and installation options for pip, Poetry and uv.

    [:octicons-arrow-right-24: Installation](installation.md)

-   :material-rocket-launch: **Quickstart**

    ---

    A complete end-to-end example to get up and running quickly.

    [:octicons-arrow-right-24: Quickstart](quickstart.md)

-   :material-bookshelf: **Concepts**

    ---

    Architecture overview and explanation of the underlying patterns.

    [:octicons-arrow-right-24: Concepts](concepts/index.md)

-   :material-book-open-variant: **Guides**

    ---

    Step-by-step guides for common tasks and use cases.

    [:octicons-arrow-right-24: Guides](guides/index.md)

-   :material-code-tags: **API Reference**

    ---

    Full API documentation, auto-generated from the source code.

    [:octicons-arrow-right-24: API Reference](reference/index.md)

</div>

## Support

If Alpha saves you time in production, consider supporting development by buying me a coffee! Your support helps me to continue improving the library and adding new features. Thank you!

<a href="https://www.buymeacoffee.com/breijling"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee&emoji=&slug=breijling&button_colour=FFDD00&font_colour=000000&font_family=Cookie&outline_colour=000000&coffee_colour=ffffff" /></a>

## Future Development Directions

### Additional Template Set For FastAPI

Planned direction: add an extra template set so `alpha api gen` can generate
FastAPI-based code in addition to the current Flask-oriented templates.

Suggested implementation outline:

- add template directory support for a FastAPI generator target
- expose this target via `--generator-name` (for example `python-fastapi`)
- document behavioral differences between Flask and FastAPI output
- provide migration notes for teams switching generator targets

### Asynchronous API Code Generation

Planned direction: add support for generating asynchronous API code, potentially via FastAPI templates.

### Asynchronous Database Support

Planned direction: add support for asynchronous database interactions, potentially via SQLAlchemy 2.0's async features.