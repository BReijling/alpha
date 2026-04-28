# Installation

This page provides instructions for installing the Alpha Python library. The basic installation includes the core functionality, while optional extras can be installed to add support for specific features or integrations.

## Basic installation

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

## Optional extras

| Extra | Description | When to use |
|---|---|---|
| `flask` | Flask + Connexion for OpenAPI-first APIs | Building REST APIs with Flask |
| `postgresql` | psycopg2 driver for PostgreSQL | Connecting to PostgreSQL databases |
| `mysql` | PyMySQL driver for MySQL | Connecting to MySQL databases |
| `ldap` | ldap3 for LDAP/Active Directory | LDAP or Active Directory authentication |
| `api-generator` | openapi-generator-cli + JDK | Generating API server code from OpenAPI specs |
