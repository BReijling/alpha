from alpha import exceptions
from alpha.infra.connectors.sql_alchemy import SqlAlchemyDatabase
from alpha.providers.models.token import Token


class DatabaseRefreshRepository:
    """Implementation of the RefreshRepository interface for database
    operations.

    This repository uses a SQLAlchemy database connector to manage refresh
    tokens in a database. It provides methods to get, create, delete, and
    delete all refresh tokens for a given subject. The tokens are stored in a
    database table which is mapped to the token model.
    """

    def __init__(
        self,
        database_connector: SqlAlchemyDatabase,
        token_model: type[Token] = Token,
        token_max_age_seconds: int = 7 * 24 * 3600,
        token_length: int = 32,
    ):
        """Initialize the DatabaseRefreshRepository with the given database
        connector and token model.

        Parameters
        ----------
        database_connector
            The database connector instance to use for database operations.
        token_model, optional
            The model class for tokens, by default Token
        token_max_age_seconds, optional
            The maximum age of a token in seconds, by default the equivalent of
            7 days in seconds
        token_length, optional
            The length of the generated token string, by default 32 characters
        """
        self._database_connector = database_connector
        self._token_model = token_model
        self._token_max_age_seconds = token_max_age_seconds
        self._token_length = token_length

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

        Raises
        ------
        NotFoundException
            If the token is not found in the database.
        """
        with self._database_connector.get_session() as session:
            result = (
                session.query(self._token_model)
                .filter_by(token=token)
                .one_or_none()
            )

            if result is None:
                raise exceptions.NotFoundException("Refresh token not found")

            return result

    def create(self, subject: str) -> Token:
        """Create a new token for a given subject.

        Parameters
        ----------
        subject
            The subject for which to create the token.

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

        with self._database_connector.get_session() as session:
            session.add(token)
            session.commit()
            session.refresh(token)
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
            If the token is not found in the database.
        """
        token_obj = self.get(token)
        with self._database_connector.get_session() as session:
            session.delete(token_obj)
            session.commit()

    def delete_all(self, subject: str) -> None:
        """Delete all tokens for a given subject.

        Parameters
        ----------
        subject
            The subject for which to delete all tokens.
        """
        with self._database_connector.get_session() as session:
            tokens = (
                session.query(self._token_model)
                .filter_by(subject=subject)
                .all()
            )
            for token in tokens:
                session.delete(token)
            session.commit()
