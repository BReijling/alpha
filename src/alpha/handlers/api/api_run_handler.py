import os
import subprocess
from typing import Any

from alpha.handlers.base_handler import BaseHandler
from alpha.exceptions import InvalidArgumentsException


class ApiRunHandler(BaseHandler):
    """Handler to run the generated API."""

    def __init__(self):
        self.api_package = None
        self.port = None

    def validate_arguments(
        self,
        api_package: str | None = None,
        port: str | int | None = None,
        **kwargs: Any,
    ) -> None:
        if api_package is None:
            raise InvalidArgumentsException(
                'Please provide a valid API package name'
            )
        if port is None:
            raise InvalidArgumentsException(
                'Please provide a valid port number'
            )

    def handle_command(self):
        """Start the API in development mode using the run-api.sh
        file.
        """
        cwd = os.getcwd()
        api_location = f'{cwd}/api'

        if not os.path.isdir(api_location):
            print("First generate the API code using 'alpha api gen'")
            return

        path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(path)
        os.environ['FLASK_ENV'] = 'development'
        os.environ['API_LOCATION'] = api_location
        os.environ['PACKAGE_NAME'] = self.api_package
        os.environ['PORT'] = str(self.port)
        subprocess.call(['sh', './run-api.sh'])
