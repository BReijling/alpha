import json
from typing import Any

from alpha import exceptions
from alpha.providers.models.token import Token


class FileRefreshRepository:
    def __init__(
        self,
        file_path: str | None = None,
        token_model: type[Token] = Token,
        token_max_age_seconds: int = 7 * 24 * 3600,
        token_length: int = 32,
    ):
        """Initialize the FileRefreshRepository with the given file path.

        Parameters
        ----------
        file_path
            File path for storing refresh tokens if using file storage,
            by default None. When the value is None the file will be stored in
            the current working directory. The file should be a JSON file that
            stores an object of refresh tokens. If the file does not exist, it
            will be created automatically. The structure of the JSON file
            should be as follows:
            ```json
            {
                "<TOKEN_VALUE>": {
                    "value": "<TOKEN_VALUE>",
                    "token_type": "Refresh",
                    "subject": "<SUBJECT>",
                    "created_at": "<ISO8601_DATETIME>",
                    "expires_at": "<ISO8601_DATETIME>"
                },
                ...
            }
            ```
        token_model
            The model class for tokens, by default Token. The model class
            should have a `from_dict` class method that takes a dictionary and
            returns an instance of the model. The dictionary will have the same
            structure as the token data in the JSON file. The model class
            should also have a `to_dict` method that converts an instance of
            the model to a dictionary with the same structure as the token data
            in the JSON file. The model class should also have a
            `create_refresh` class method that creates a new refresh token.
        token_max_age_seconds
            The maximum age of a token in seconds, by default the equivalent of
            7 days in seconds
        token_length
            The length of the generated token string, by default 32 characters
        """
        self._file_path = file_path or "refresh_tokens.json"
        self._token_model = token_model
        self._token_max_age_seconds = token_max_age_seconds
        self._token_length = token_length

        with open(self._file_path, "a+") as file:
            file.seek(0)
            try:
                json.load(file)
            except json.JSONDecodeError:
                file.seek(0)
                file.write("{}")
                file.truncate()

    def get(self, token: str) -> Token:
        """Get a token by its value.

        Parameters
        ----------
        token
            The value of the token to retrieve.

        Returns
        -------
        Token
            The token object corresponding to the given value.
        """
        with open(self._file_path, "r") as file:
            tokens_data: dict[str, dict[str, Any]] = json.load(file)
            token_data = tokens_data.get(token, None)

            if not token_data:
                raise exceptions.NotFoundException("Refresh token not found")

            return self._token_model.from_dict(token_data)

    def create(self, subject: str) -> Token:
        """Create a new token for a given subject.

        Parameters
        ----------
        subject
            The subject for which to create a new token.

        Returns
        -------
        Token
            The newly created token object.
        """
        token = self._token_model.create_refresh(
            subject=subject,
            max_age_seconds=self._token_max_age_seconds,
            token_length=self._token_length,
        )

        with open(self._file_path, "r") as file:
            tokens_data: dict[str, dict[str, Any]] = json.load(file)

        tokens_data[token.value] = token.to_dict()

        with open(self._file_path, "w") as file:
            json.dump(tokens_data, file, indent=4)

        return token

    def delete(self, token: str) -> None:
        """Delete a token by its value.

        Parameters
        ----------
        token
            The value of the token to delete.

        Raises
        ------
        NotFoundException
            If the token with the given value is not found in the file.
        """
        with open(self._file_path, "r") as file:
            tokens_data: dict[str, dict[str, Any]] = json.load(file)

        if token in tokens_data:
            del tokens_data[token]

            with open(self._file_path, "w") as file:
                json.dump(tokens_data, file, indent=4)
        else:
            raise exceptions.NotFoundException("Refresh token not found")

    def delete_all(self, subject: str) -> None:
        """Delete all tokens for a given subject.

        Parameters
        ----------
        subject
            The subject for which to delete all tokens.
        """
        with open(self._file_path, "r") as file:
            tokens_data: dict[str, dict[str, Any]] = json.load(file)

        tokens_to_delete = [
            token
            for token, data in tokens_data.items()
            if data["subject"] == subject
        ]

        if not tokens_to_delete:
            return None

        for token in tokens_to_delete:
            del tokens_data[token]

        with open(self._file_path, "w") as file:
            json.dump(tokens_data, file, indent=4)
