# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.5] - 2026-01-15

### Added

- `ADProvider` class for AD identity providers. The class extends the `LDAPProvider` class and overrides the default parameter values.
- `AD_SEARCH_ATTRIBUTES` constant which are used by default by the ADProvider class.
- Imports of all classes and functions at root module level.

### Fixed

- Unable to merge attributes of a User object to an Identity object due to a wrong parameter name.

## [0.2.4] - 2026-01-13

### Fixed

- Previously, the base image in the `Dockerfile.mustache` template was hardcoded, which made it impossible to use a base image other than the default base image `python:3.13`. Now, it is possible to pass a different base image as a build argument

## [0.2.3] - 2026-01-12

### Fixed

- missing imports in `__main__.mustache` template.

## [0.2.2] - 2026-01-12

### Fixed

- When the api cli is being used from a folder which does not contain a `src` folder the guessed input options contain `None`. The `_guess_current_package_name` function now looks for a `pyproject.toml` file from which the package name is fetched. If the file is not present, it scans the subfolders for a python project. The current folder name is used as a fallback

## [0.2.1] - 2026-01-12

### Fixed

- Shell scripts for api code generation are not packaged.

## [0.2.0] - 2026-01-11

Minor release with added features. An identity provider for LDAP and a cli interface for generating and running API code by using mustache templates.

### Added

- Interfaces for identity providers
- JWTFactory
- JWTProvider mixin
- LDAPConnector
- LDAPProvider
- AuthenticationService
- ApiGenerateHandler
- ApiRunHandler

## [0.1.0] - 2026-01-10 [YANKED]

Initial release

### Added

- adapters
- domain.models
- factories
- factories.models
- infra.databases
- infra.models
- interfaces
- repositories
- repositories.models
- utils
- encoder.py
- exceptions.py
