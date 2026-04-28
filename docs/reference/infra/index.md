# API Reference - Infra

Reference documentation for all Infra classes and functions.

All documentation is auto-generated from docstrings in the source code.

## Connectors

| Connector | Description |
|---|---|
| [SqlAlchemyDatabase](connectors/sql_alchemy.md) | SQL Alchemy Database Connector |
| [LDAPConnector](connectors/ldap_connector.md) | LDAP connector |
| [OIDCConnector](connectors/oidc_connector.md) | OIDC connector |
| [KeyCloakOIDCConnector](connectors/keycloak_connector.md) | Keycloak OIDC connector |

## Models

| Model | Description |
|---|---|
| [SearchFilter](models/search_filter.md) | Query search/filter model |
| [Operator](models/operator.md) | Enumeration of possible operators for search filters |
| [FilterOperators](models/filter_operators.md) | Supported query filter operators |
| [OrderBy](models/order_by.md) | Query ordering model |
| [Order](models/order.md) | Enumeration of possible ordering directions (ascending/descending) |
| [JsonPatch](models/json_patch.md) | JSON patch model |
| [QueryClause](models/query_clause.md) | A base class representing a query clause for SQLAlchemy queries |