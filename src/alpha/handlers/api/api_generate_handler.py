import hashlib
import os
import shutil
import subprocess
import time
from typing import Any, Optional

# import yaml

from alpha.handlers.base_handler import BaseHandler
from alpha.exceptions import InvalidArgumentsException


class ApiGenerateHandler(BaseHandler):
    """Handler to generate the api based on a OpenAPI docker generator.
    Watching the spec file and post process file for changes.
    """

    def __init__(self) -> None:
        self.spec_file = None
        self.api_package = None
        self.service_package = None
        self.container_import = None
        self.init_container_from = None
        self.init_container_function = None
        self.post_process_file = None
        self.no_watch = False
        self.no_docker = False
        self.permissions_only = False
        self.templates_only = False
        self.templates_folder = 'templates'
        self.output_folder = 'api'
        self.generator_name = None
        self.reserved_words_mappings = ['date', 'field']

        self.cwd = os.getcwd()
        self.module_path = os.path.dirname(os.path.realpath(__file__))
        self.project_templates_folder = os.path.join(self.cwd, 'templates')

    def validate_arguments(
        self,
        spec_file: Optional[str] = None,
        api_package: Optional[str] = None,
        service_package: Optional[str] = None,
        post_process_file: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        if (
            spec_file is None
            or post_process_file is None
            or api_package is None
            or service_package is None
        ):
            raise InvalidArgumentsException(
                '\n\nDubbelcheck alle opgegeven parameters, ben je in de'
                ' juiste map aan het werk? De packagenaam kan namelijk niet'
                ' automatisch worden afgeleid\n'
            )

    def handle_command(self) -> None:
        """Handling the 'api gen' command.

        Watching file until its hash is changed. When hash changes, run the
        bash-file to generate the API.

        - Skipping the watch process when the 'no-watch' argument is used.
        - Only creating a permissions file when the 'permissions-only' argument
        is used.
        - Only copying the mustache templates to a templates folder in the
        working directory when the 'templates-only' argument is used.
        - Only returning generator arguments when the
        'generator-arguments-only' argument is used.
        """

        self.permissions_file_path = (
            f'{self.cwd}/api/{self.api_package}/config/permissions.yaml'
        )

        # Return early exit if only templates are needed
        if self.templates_only:
            self._copy_templates()
            print('Done copying templates folder to project directory.')
            return

        if not os.path.isfile(str(self.spec_file)):
            print(
                f"Given specification file '{self.spec_file}' does not exist"
            )
            return

        # Return early exit if only permissions are needed
        if self.permissions_only:
            # self._generate_configuration()
            # print(f'Done generating {self.permissions_file_path} file.')
            return

        # Return early exit if the watch process is undesirable
        if self.no_watch:
            self._run_generator()
            print('Done generating API code.')
            return

        files_to_watch = [str(self.spec_file), str(self.post_process_file)]
        hash_string = None
        try:
            while True:
                hash = hashlib.md5()
                for file_name in files_to_watch:
                    if not os.path.isfile(file_name):
                        continue
                    hash.update(open(file_name, 'rb').read())

                new_hash_string = hash.hexdigest()

                if new_hash_string == hash_string:
                    time.sleep(1)
                    continue

                hash_string = new_hash_string
                self._run_generator()
                print('Done generating.')

                print(
                    f"Watching '{self.spec_file}' and"
                    f" '{self.post_process_file}' for package"
                    f" '{self.service_package}'"
                )
        except KeyboardInterrupt:
            print('Stopped watching')

    def _run_generator(self) -> None:
        """Run the generator, based on docker, using the gen-code.sh file."""
        # Change paths to open api folder and define paths for
        # working directory. Put everyting in env-vars to be used whitin
        # the bash file

        # Generate permissions
        # self._generate_configuration()

        os.chdir(self.module_path)
        os.environ['WORKING_DIR'] = self.cwd
        os.environ['SPEC_FILE'] = str(self.spec_file)
        os.environ['GENERATOR_NAME'] = str(self.generator_name)
        os.environ['PACKAGE_NAME'] = str(self.api_package)
        os.environ['SERVICE_PACKAGE'] = str(self.service_package)
        os.environ['FLASK_ENV'] = 'development'
        os.environ['CONTAINER_IMPORT'] = str(self.container_import)
        os.environ['INIT_CONTAINER_FROM'] = str(self.init_container_from)
        os.environ['INIT_CONTAINER_FUNCTION'] = str(
            self.init_container_function
        )
        os.environ['RESERVED_WORDS_MAPPINGS'] = ' '.join(
            [
                f'--reserved-words-mappings={word}={word}'
                for word in self.reserved_words_mappings
            ]
        )

        self._copy_templates()

        # Calling generate code shell script
        subprocess.call(['bash', './gen-code.sh'])

        self._remove_templates()

        os.chdir(self.cwd)

        # Run post process file of the current project
        post_process_file = f'{self.cwd}/{self.post_process_file}'
        if os.path.isfile(post_process_file):
            print('Found post process, running...')
            subprocess.call(['python3', post_process_file])
        else:
            print(f'No post process file ({self.post_process_file}) found')

    # def _generate_configuration(self) -> None:
    #     """Generate permission.yaml file for the /configuration endpoint."""

    #     PERMISSION_FILE = (
    #         f'{self.cwd}/api/{self.api_package}/config/permissions.yaml'
    #     )
    #     os.makedirs(os.path.dirname(PERMISSION_FILE), exist_ok=True)

    #     permissions = {}
    #     with open(str(self.spec_file), 'r') as stream:
    #         try:
    #             data = yaml.safe_load(stream)
    #             parser = YamlParser()
    #             permissions = {  # type: ignore
    #                 'version': data['info']['version'],
    #                 'endpoints': parser.parse_endpoints(data),
    #             }
    #         except yaml.YAMLError as exc:
    #             print(exc)

    #     with open(PERMISSION_FILE, 'w+') as file:
    #         yaml.dump(data=permissions, stream=file)

    def _copy_templates(self) -> None:
        """Copy mustache templates to the templates folder in the working
        directory
        """
        shutil.rmtree(self.project_templates_folder, ignore_errors=True)
        shutil.copytree(
            src=os.path.join(
                self.module_path, self.templates_folder, self.generator_name
            ),
            dst=self.project_templates_folder,
            dirs_exist_ok=True,
        )
        return

    def _remove_templates(self) -> None:
        """Cleanup the templates folder in the working directory"""
        shutil.rmtree(self.project_templates_folder)
        return
