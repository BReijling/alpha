# Alpha

Alpha is intended to be the first dependency you need to add to your Python application. It is a Python library which contains standard building blocks that can be used in applications that are used as APIs and/or make use of database interaction.

## Badges

[![PyPI version](https://img.shields.io/pypi/v/alpha-python.svg)](https://pypi.org/project/alpha-python/)
[![Build Status](https://github.com/breijling/alpha/actions/workflows/python-app.yml/badge.svg?branch=main)](https://github.com/breijling/alpha/actions/workflows/python-app.yml)
[![Coverage Status](https://coveralls.io/repos/github/BReijling/alpha/badge.svg?branch=main)](https://coveralls.io/github/BReijling/alpha?branch=main)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

## Documentation

[![Documentation Status](https://readthedocs.org/projects/alpha-python/badge/?version=latest)](https://alpha-python.readthedocs.io/en/latest/)

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

## Usage

The library contains a lot of different components, but the most important ones are:

- `alpha.encoder.JSONEncoder`: A JSON encoder that can be used to serialize complex objects to JSON.

## Features



## Contributing

If you want to contribute to the development of this library, you can fork the repository and create a pull request with your changes.

## License

This library is licensed under the MIT License. See the LICENSE file for more information.
