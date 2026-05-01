# Quickstart

This quickstart helps you go from an OpenAPI file to a running local API using Alpha. A working example of the code generated in this quickstart can be found in the example folder of the [Alpha repository](https://github.com/breijling/alpha/tree/main/example).

## What you will build

By the end of this page, you will have:

- Alpha installed with API generation support
- a minimal OpenAPI specification
- generated API code in an `api/` folder
- a local development server running on `http://localhost:8080`

## Prerequisites

- Python 3.11+
- `uv` (for this example, but you can use any Python environment manager)

## 1. Create a project structure

Create a new directory for your project, navigate into it and initialize a new project:

```shell
mkdir <project_name>
cd <project_name>
uv init --package --name <project_name> 
```

Add the `alpha` dependencies to your project:

```shell
uv add alpha-python --extra flask
uv add --dev alpha-python --extra api-generator
```

Create the folders used by the generator:

```shell
mkdir -p specification
```

Create `specification/openapi.yaml` and add a minimal API:

```yaml
openapi: 3.0.0
info:
  title: <project_name> API
  version: 0.1.0
servers:
  - url: http://localhost:8080
paths:
  /:
    get:
      operationId: health_check
      x-alpha-custom-function: 'dict(status="ok")'
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    example: ok
```

## 2. Generate API code

Run the generator in development mode:

```shell
uv run alpha api gen
```

What this does:

- reads `specification/openapi.yaml`
- generates (or updates) code in `api/`
- starts a watch loop so changes in the spec are re-generated automatically

If you only want to generate once:

```shell
uv run alpha api gen --no-watch
```

Install the generated API package in your environment in editable mode:

```shell
uv pip install -e api/
```

## 3. Implement business logic

Create at least the following files:

- `src/<project_name>/containers/__init__.py`
- `src/<project_name>/containers/container.py`
- `src/<project_name>/__init__.py`

With the following content:

In `src/<project_name>/containers/container.py`:

```python
from dependency_injector import containers, providers

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
```

In `src/<project_name>/__init__.py`:

```python
from <project_name>.containers.container import Container


def init_container() -> Container:
    container = Container()
    container.config.from_dict({"cors": {"origins": ["*"]}})

    container.wire(modules=[__name__])
    return container
```

## 4. Run the API

In a second terminal:

```shell
uv run alpha api run
```

The generated API should now be available at `http://localhost:8080`.

The Swagger UI should be available at `http://localhost:8080/ui`.

## 5. Test your endpoint

Use `curl` to verify everything works:

```shell
curl -s http://localhost:8080/
```

Expected response:

```json
{
  "data": {
    "status": "ok"
  },
  "detail": "OK",
  "status": 200,
  "title": "OK",
  "type": "application/json"
}
```

## 6. Iterate quickly

Keep both commands running during development:

1. `uv run alpha api gen` (watch mode)
2. `uv run alpha api run`

Then update your OpenAPI file and implement business logic in the generated service layer.

## Next steps

- Learn how to design your application architecture in the [Design Principles guide](concepts/design-principles.md)
- Learn how to implement business logic in the [Dependency Injection guide](concepts/dependency-injection.md)
- Continue with the full [API Generation guide](guides/api-generation.md)
- Add authentication via [Authentication guide](guides/authentication.md)
- Add persistence via [Database interaction guide](guides/database-interaction.md)
