# API Reference - Interfaces

Reference documentation for all Interface definitions and protocols.

All documentation is auto-generated from docstrings in the source code.

## Data Access

| Interface | Description |
|---|---|
| [UnitOfWork](unit_of_work.md) | Unit of Work contract for transaction scopes |
| [SqlDatabase](sql_database.md) | SQL database abstraction interface |
| [SqlRepository](sql_repository.md) | Repository interface for SQL backends |
| [ApiRepository](api_repository.md) | Repository interface for REST API backends |
| [SqlMapper](sql_mapper.md) | SQL mapper interface for model persistence |

## Model Protocols

| Protocol | Description |
|---|---|
| [OpenAPIModel](openapi_model.md) | Protocol for OpenAPI-generated models |
| [AttrsInstance](attrs_instance.md) | Protocol for attrs-based model instances |
| [DataclassInstance](dataclass_instance.md) | Protocol for dataclass-based model instances |
| [PydanticInstance](pydantic_instance.md) | Protocol for pydantic-based model instances |

## Object Manipulation

| Interface | Description |
|---|---|
| [Updatable](updatable.md) | Contract for update operations on models |
| [Patchable](patchable.md) | Contract for patch operations on models |

## Authentication

| Interface | Description |
|---|---|
| [Providers](providers.md) | Authentication provider interface |
| [TokenFactory](token_factory.md) | Token factory interface |
