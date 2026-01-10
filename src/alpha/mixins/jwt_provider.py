"""Mixin for token issuance and validation using a TokenFactory."""

from alpha import exceptions
from alpha.interfaces.token_factory import TokenFactory
from alpha.providers.models.identity import Identity
from alpha.providers.models.token import Token


class JWTProviderMixin:
    """Mixin class to add token issuance and validation capabilities
    using a TokenFactory.
    """

    _token_factory: TokenFactory | None = None

    def validate(self, token: Token) -> Identity:
        """Validate a token and return the associated identity

        Parameters
        ----------
        token
            Token object to be validated

        Returns
        -------
            Identity object representing the subject
        """
        if not self._token_factory:
            raise exceptions.MissingDependencyException(
                "Token factory is not configured"
            )

        try:
            self._token_factory.validate(token.value)
        except Exception as e:
            raise e

        payload = self._token_factory.get_payload(token.value)
        subject = payload.get("subject")

        if not subject:
            raise ValueError(
                "Token payload does not contain mandatory \'subject\' field"
            )

        return Identity.from_dict(payload)

    def issue_token(self, identity: Identity) -> Token:
        """Issue a token for the given identity

        Parameters
        ----------
        identity
            Identity object for which to issue a token

        Returns
        -------
            Token object
        """
        if not self._token_factory:
            raise exceptions.MissingDependencyException(
                "Token factory is not configured"
            )

        payload = identity.to_dict()
        token_value = self._token_factory.create(
            subject=identity.subject, payload=payload
        )
        return Token(token_value, token_type="Bearer")
