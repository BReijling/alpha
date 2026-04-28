# API Generation

In this guide, you will learn how to scaffold and iterate on a API, based on an OpenAPI specification, using Alpha's API generation capabilities. The API generator creates controller code that maps HTTP requests to service method calls, based on the structure and metadata defined in your OpenAPI file. This allows you to focus on implementing your business logic in service classes while the generator handles the boilerplate of request parsing, response formatting, and endpoint wiring.

These are the main steps to get started with API generation:

- Generate code with `alpha api gen`
- Run generated code in development mode with `alpha api run`

## What You Will Learn

- How to generate API code from an OpenAPI file
- How the watch loop works during development
- Which CLI options are most important
- How `x-alpha-*` vendor extensions influence generated endpoint behavior

## Prerequisites

Install Alpha with API generator support:

```shell
pip install alpha-python[api-generator]
```

Or with Poetry/uv:

```shell
poetry add --dev alpha-python --extras api-generator
uv add --dev alpha-python --extra api-generator
```

Minimal project inputs:

- an OpenAPI spec (default path: `specification/openapi.yaml`)
- optionally a post-processing script (default path: `post_process.py`)

## Development Workflow

1. Create or update your OpenAPI file.
2. Run generation in watch mode:

```shell
alpha api gen
```

3. Start the generated API:

```shell
alpha api run
```

4. Iterate on the OpenAPI file. The generator reruns automatically when watched files change.

### One-Shot Generation

Use this when you do not want a watch loop:

```shell
alpha api gen --no-watch
```

## CLI Reference

### `alpha api gen`

Generate API code into the `api/` folder.

Common options:

| Option | Default | Description |
|---|---|---|
| `--spec-file` | `specification/openapi.yaml` | Path to your OpenAPI specification |
| `--api-package` | auto-guessed | Package name for generated API code |
| `--service-package` | auto-guessed | Package containing your service layer |
| `--container-import` | auto-guessed | Import statement for the DI container |
| `--init-container-from` | auto-guessed | Module path where init function is imported from |
| `--init-container-function` | `init_container` | Name of DI initialization function |
| `--post-process-file` | `post_process.py` | Script executed after generation |
| `--generator-name` | `python-flask` | OpenAPI generator template set |
| `--no-watch` | `false` | Run once instead of watching files |
| `--templates-only` | `false` | Only copy templates, do not generate API code |

Notes:

- Package names are guessed from `pyproject.toml` when possible.
- If guessing is wrong, override with explicit CLI options.

### `alpha api run`

Run the generated API in development mode.

| Option | Default | Description |
|---|---|---|
| `--api-package` | auto-guessed | Generated API package name |
| `--port` | `8080` | Port to run the API on |

Example:

```shell
alpha api run --port 8081
```

## Vendor Extensions

Alpha supports multiple `x-alpha-*` extensions to customize endpoint behavior.

### Extension Overview

| Extension | Scope | Purpose |
|---|---|---|
| `x-alpha-service-name` | operation | Service dependency to call |
| `x-alpha-service-method` | operation | Method name on the service |
| `x-alpha-request-factory` | operation | Execute call via `RequestFactory` |
| `x-alpha-custom-function` | operation | Use a custom callable/expression |
| `x-alpha-service-additional-parameters` | operation | Forward extra runtime parameters |
| `x-alpha-import` | operation | Add imports to generated controller |
| `x-alpha-factory` | operation | Convert request body model to custom object |
| `x-alpha-verify-roles` | operation | Role based access constraint |
| `x-alpha-verify-groups` | operation | Group based access constraint |
| `x-alpha-verify-permissions` | operation | Permission based access constraint |
| `x-alpha-filelist` | body parameter | Build list of uploaded files |
| `x-alpha-response-factory` | response | Convert service output to response model |
| `x-alpha-raw-response` | response | Return service result as-is |
| `x-alpha-cookie-support` | response | Enable cookie-aware response object |
| `x-alpha-debug-response` | response | Debug-log response payload |
| `x-alpha-exception` | response | Map custom exception class to status code |

### `x-alpha-service-name`

Defines which injected service instance is called by the generated endpoint.

```yaml
paths:
  /users:
    get:
      x-alpha-service-name: user_management_service
      x-alpha-service-method: get_users
```

### `x-alpha-service-method`

Defines the method that is invoked on `x-alpha-service-name`.

```yaml
paths:
  /users/{user_id}:
    get:
      x-alpha-service-name: user_management_service
      x-alpha-service-method: get_user
```

### `x-alpha-request-factory`

When `true`, the generated code wraps the service call via `RequestFactory`.

```yaml
paths:
  /users:
    post:
      x-alpha-service-name: user_management_service
      x-alpha-service-method: add_user
      x-alpha-request-factory: true
```

### `x-alpha-custom-function`

Bypasses normal service dispatch and executes a custom callable/expression.

```yaml
paths:
  /health:
    get:
      x-alpha-custom-function: str("ok")
```

### `x-alpha-service-additional-parameters`

Passes extra runtime values to the service method. Typical values are
`auth_token`, `refresh_token`, or `api_key`.

```yaml
paths:
  /auth/refresh:
    patch:
      x-alpha-service-name: authentication_service
      x-alpha-service-method: refresh_token
      x-alpha-service-additional-parameters:
        - auth_token
        - refresh_token
```

### `x-alpha-import`

Adds one or more import lines directly to the generated controller function.

```yaml
paths:
  /users:
    post:
      x-alpha-import:
        - from my_app.models import UserModel
      x-alpha-factory: UserModel.factory
```

### `x-alpha-factory`

Applies a factory callable to request body model data before calling the service
method.

```yaml
paths:
  /pets:
    post:
      x-alpha-import:
        - from my_app.models import PetModel
      x-alpha-factory: PetModel.factory
      x-alpha-service-name: pet_service
      x-alpha-service-method: add_pet
```

### `x-alpha-verify-roles`

Requires one of the configured roles on authenticated identity.

```yaml
paths:
  /admin/users/{user_id}:
    delete:
      x-alpha-verify-roles:
        - admin
        - superuser
```

### `x-alpha-verify-groups`

Requires membership in one of the configured groups.

```yaml
paths:
  /users/{user_id}:
    put:
      x-alpha-verify-groups:
        - admins
        - support
```

### `x-alpha-verify-permissions`

Requires one or more permissions before the endpoint logic runs.

```yaml
paths:
  /users/{user_id}:
    put:
      x-alpha-verify-permissions:
        - READ
        - WRITE
```

### `x-alpha-filelist`

Marks a file/body parameter as a list of files so generated code reads all
multipart files into a Python list.

```yaml
paths:
  /documents/upload:
    post:
      requestBody:
        required: true
        x-alpha-filelist: true
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                files:
                  type: array
                  items:
                    type: string
                    format: binary
      x-alpha-service-name: document_service
      x-alpha-service-method: upload
```

### `x-alpha-response-factory`

Converts service output into a target response class before returning the HTTP
response.

```yaml
paths:
  /users:
    get:
      responses:
        '200':
          description: OK
          x-alpha-response-factory: list[api_models.User]
```

### `x-alpha-raw-response`

Returns the service result directly, skipping standard response object
construction.

```yaml
paths:
  /proxy:
    get:
      responses:
        '200':
          description: OK
          x-alpha-raw-response: true
```

### `x-alpha-cookie-support`

Enables cookie-aware response handling (for example setting or deleting cookies
in auth flows).

```yaml
paths:
  /auth/login:
    post:
      responses:
        '201':
          description: Created
          x-alpha-cookie-support: true
```

### `x-alpha-debug-response`

Logs the response payload on debug log level.

```yaml
paths:
  /pets/{pet_id}:
    get:
      responses:
        '200':
          description: OK
          x-alpha-debug-response: true
```

### `x-alpha-exception`

Maps a custom exception class to the response status code where the extension is
defined.

```yaml
paths:
  /pets:
    post:
      x-alpha-import:
        - from my_app.exceptions import InvalidInstance
      responses:
        '422':
          description: Unprocessable Content
          x-alpha-exception: InvalidInstance
```

### Combined Example

```yaml
paths:
  /users:
    get:
      operationId: get_users
      x-alpha-service-name: user_management_service
      x-alpha-service-method: get_users
      x-alpha-verify-permissions:
        - READ
      responses:
        '200':
          description: OK
          x-alpha-response-factory: list[api_models.User]
```

## Output And Folder Conventions

- Generated API output is placed in `api/`
- Temporary templates are copied into `templates/` during generation
- Optional post-processing runs after generation if `post_process.py` exists

## Troubleshooting

### OpenAPI generator not installed

If `alpha api gen` reports missing OpenAPI Generator CLI, reinstall with the `api-generator` extra.

### API run fails with missing `api/` folder

Generate first:

```shell
alpha api gen --no-watch
```

### Wrong package/container guesses

Pass explicit values for:

- `--api-package`
- `--service-package`
- `--container-import`
- `--init-container-from`
- `--init-container-function`

To see what the generator guessed, run with `--help` to view all options.

## End-to-End Example Project

This example shows a minimal path from an empty folder to a running generated
API.

### 1. Create a project skeleton

```text
my-api-project/
  pyproject.toml
  specification/
    openapi.yaml
```

Use a package name in `pyproject.toml` (for example `my_api_project`). Alpha
uses this to guess `--api-package` and `--service-package` defaults.

### 2. Add a minimal OpenAPI file

```yaml
openapi: 3.0.0
info:
  title: Minimal API
  version: 0.1.0
paths:
  /health:
    get:
      operationId: health
      x-alpha-custom-function: str("ok")
      responses:
        '200':
          description: OK
```

### 3. Generate code

```shell
alpha api gen --no-watch
```

### 4. Run the generated API

```shell
alpha api run
```

### 5. Iterate during development

Switch to watch mode when actively editing the specification:

```shell
alpha api gen
```

In another terminal, keep the API running with `alpha api run`.

## Recommended Project Layout

Use a clear separation between transport (generated API), orchestration
(services), and wiring (container).

```text
my_api_project/
  specification/
    openapi.yaml
  src/
    my_api_project/
      containers/
        __init__.py
        container.py
      services/
        __init__.py
        model_management_service.py
      __init__.py
  api/
    my_api_project_api/
      controllers/
      models/
      openapi/
  pyproject.toml
```

Recommended conventions:

- Keep the OpenAPI spec in `./specification/openapi.yaml` to avoid confusion with generated code.
- Keep business logic in `./src/<package_name>/services/`, not in generated controllers.
- Keep generated code in `./api/` and treat it as build output.
- Add `api/` to `.gitignore` if you do not want generated code in version control.
- Register service dependencies in `./src/<package_name>/containers/container.py`.
- Define an `init_container` function in `./src/<package_name>/__init__.py` to initialize the DI container.
- Use `x-alpha-service-name` and `x-alpha-service-method` as stable contract
  between OpenAPI operations and service methods.
- Use `./post_process.py` optionally for deterministic project-specific patching.

## Future Development Directions

### Additional Template Set For FastAPI

Planned direction: add an extra template set so `alpha api gen` can generate
FastAPI-based code in addition to the current Flask-oriented templates.

Suggested implementation outline:

- add template directory support for a FastAPI generator target
- expose this target via `--generator-name` (for example `python-fastapi`)
- document behavioral differences between Flask and FastAPI output
- provide migration notes for teams switching generator targets
