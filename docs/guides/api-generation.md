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

Or add it to your project with poetry/uv:

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
| `x-alpha-custom-response-builder` | operation | Use a custom callable/expression for final response object building |
| `x-alpha-verify-roles` | operation | Role based access constraint |
| `x-alpha-verify-groups` | operation | Group based access constraint |
| `x-alpha-verify-permissions` | operation | Permission based access constraint |
| `x-alpha-filelist` | body parameter | Build list of uploaded files |
| `x-codegen-request-body-name` | body parameter | Specify the name of the request body model |
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

Bypasses normal service dispatch and executes a custom callable/expression. The value needs to be escaped using single quotes when double quotes are used in the expression, for example `x-alpha-custom-function: '"123"'` or `x-alpha-custom-function: 'str("ok")'`.

```yaml
paths:
  /health:
    get:
      x-alpha-custom-function: '"ok"'
```

### `x-alpha-service-additional-parameters`

Passes extra runtime values to the service method. The additional parameters are passed as keyword arguments to the service method, and the values are extracted from the request context.

Available values include:
 - `identity` ([`Identity`][alpha.providers.models.identity.Identity]): The Identity object of the authenticated user, if available.
 - `payload` (dict[str, Any]): The raw payload of the authenticated user, if available.
 - `headers` ([`Headers`][alpha.utils.request_headers.Headers]): The Headers object which contains authentication headers and cookies, if available.
 - `auth_token` (str): The value of the `Authorization` header, if available.
 - `refresh_token` (str): The value of the `Refresh-Token` header, if available.
 - `api_key` (str): The value of the `X-API-Key` header, if available.
 - `cookies` (dict[str, str]): All request cookies, if available.

```yaml
paths:
  /auth/refresh:
    patch:
      x-alpha-service-name: authentication_service
      x-alpha-service-method: refresh_token
      x-alpha-service-additional-parameters:
        - auth_token
        - refresh_token
  /objects:
    get:
      x-alpha-service-name: object_service
      x-alpha-service-method: get_objects
      x-alpha-service-additional-parameters:
        - identity
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

### `x-alpha-custom-response-builder`

Use a custom function to build the final response object, instead of the default behavior. The generated controller calls the custom function with the same keyword arguments used to build the response object via `create_response_object(...)`, for example `http_codes`, `status_code`, `status_message`, `data`, and, when applicable, exception-related fields. This means the callable should accept the named arguments the generator provides, either explicitly or via `**kwargs` (for example, `def response_builder(**kwargs): ...`). The same builder is used for both normal and exception responses, so it must be able to handle both cases. Check the [Response Object reference](../reference/utils/create_response_object.md) for details on the expected fields and return format. This value can either be a direct callable (for example `my_response_builder`), a dotted path to a callable (`my_app.utils.response_builder`), a classmethod or a staticmethod.

```yaml
paths:
  /users/{user_id}:
    get:
      x-alpha-service-name: user_service
      x-alpha-service-method: get_user
      x-alpha-import:
        - from my_app.utils import response_builder
      x-alpha-custom-response-builder: response_builder
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

Requires one or more permissions before the endpoint logic runs. When multiple permissions are listed, all of them are required (logical AND).

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

### `x-codegen-request-body-name`

Specifies the name of the request body model class generated from the OpenAPI spec. This is useful when you want to control the naming of the request body model, especially when the default naming might not be suitable or conflicts with existing classes.

```yaml
  /users:
    post:
      requestBody:
        x-codegen-request-body-name: CustomUser
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/User'
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

## Endpoint authentication and authorization

The generated API does not enforce any specific authentication or authorization mechanism by default, but it provides flexible options to implement these features based on your application's needs. You can use the `x-alpha-verify-roles`, `x-alpha-verify-groups`, and `x-alpha-verify-permissions` vendor extensions to define coarse- or fine-grained access constraints on a per-endpoint basis. The generator will then include the necessary checks in the generated controller code, allowing you to integrate with your existing authentication and authorization system.

In order to verify an access token and extract user information for authorization checks, a token factory is required. The generated API looks for a token factory in the DI container under the name `token_factory`. This factory should implement a method to validate the token and a method to get the payload from the token. An example of how to setup the token factory in the container is shown in the [Authentication guide](../guides/authentication.md#example-implementation). In order to use the `x-alpha-verify-roles`, `x-alpha-verify-groups`, or `x-alpha-verify-permissions` extensions, the token factory must be able to extract the relevant information (for example roles, groups, permissions) from the token payload.

To enable authentication, a security scheme needs to be defined in the OpenAPI specification. Furthermore, each endpoint can specify the required security schemes using the `security` field. Below is an example of how to define a bearer token security scheme and require it for an endpoint, along with permission-based access control using `x-alpha-verify-permissions`:

```yaml
paths:
  /objects:
    get:
      description: Get list of objects
      operationId: get_objects
      responses:
        '200':
          description: OK
      tags: [Objects]
      x-alpha-service-name: object_service
      x-alpha-service-method: get_objects
      x-alpha-verify-permissions:
        - READ_OBJECTS
      security:
        - bearerAuth: []
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

## End-to-End Example Project

Check out the [quickstart guide](../quickstart.md) for a complete example of API generation, including a sample OpenAPI spec and implementation of business logic.

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

## Configuring CORS and Response Headers

The generated API supports CORS and custom response headers via configuration in the DI container. You can set these values in your container configuration, for example:

```python
# src/my_api_project/__init__.py
from my_api_project.containers.container import Container

def init_container() -> Container:
    container = Container()

    container.config.cors.origins = ["https://example.com"]
    container.config.response.headers = {
        "X-Custom-Header": "MyValue"
    }

    container.wire(modules=[__name__])
    return container
```

When CORS origins are not configured, the generated API defaults to allowing all origins (`*`) and logs a warning. 

Custom response headers defined in the container configuration are added to all responses. When no custom response headers are configured, the following headers are added:

- `Cache-Control: no-store`
- `Content-Security-Policy: default-src 'self'`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`

When a request is made to the Swagger UI (`/ui`), the generator skips adding any response headers that have "Content-Security-Policy" in their name to avoid breaking the UI.
