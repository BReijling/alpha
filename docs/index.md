# Alpha

**Alpha** is a foundational Python library providing standard building blocks for Python applications that use APIs and/or database interactions.

[![PyPI version](https://badge.fury.io/py/alpha-python.svg)](https://badge.fury.io/py/alpha-python)
[![Documentation Status](https://readthedocs.org/projects/alpha-python/badge/?version=latest)](https://alpha-python.readthedocs.io/en/latest/)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

---

## Core features

- **JSON Serialization** — `JSONEncoder` for complex types: numpy, pandas, datetime, UUID, Enums and objects with `to_dict()`
- **Authentication & Authorization** — OIDC/KeyCloak, LDAP/Active Directory, JWT and password-based authentication
- **Database access layer** — SQLAlchemy abstraction with Repository and Unit of Work patterns
- **API development** — OpenAPI code generation via CLI, Flask integration, request/response utilities
- **Dependency Injection** — YAML-configurable DI container built on `dependency-injector`
- **Model support** — Domain models with audit trail, attrs, Pydantic, dataclasses and OpenAPI model support

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
    repo = uow.get_repository(MyRepository)
    items = repo.get_all()
    uow.commit()
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

-   :material-book-open-variant: **Concepts**

    ---

    Architecture overview and explanation of the underlying patterns.

    [:octicons-arrow-right-24: Concepts](concepts/index.md)

-   :material-code-tags: **API Reference**

    ---

    Full API documentation, auto-generated from the source code.

    [:octicons-arrow-right-24: API Reference](reference/index.md)

</div>
