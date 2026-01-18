"""OIDC connectors."""

from __future__ import annotations

from typing import Any, Mapping, cast
from urllib.parse import urljoin

import requests
from requests.auth import HTTPBasicAuth

from alpha import exceptions


class OIDCConnector:
    """OIDC connector for interacting with an OpenID Connect identity provider
    via OIDC/OAuth2 protocols.

    Parameters
    ----------
    token_url
        Token endpoint URL or relative path.
    userinfo_url
        Optional userinfo endpoint URL or relative path.
    introspection_url
        Optional token introspection endpoint URL or relative path.
    client_id
        OAuth2 client identifier used for token requests.
    client_secret
        OAuth2 client secret used for token requests.
    scope
        Space-delimited OAuth2 scopes for standard token requests.
    verify_tls
        Whether to verify TLS certificates for HTTP requests.
    timeout_seconds
        Request timeout in seconds.
    use_basic_auth
        Whether to send client credentials via HTTP Basic Auth.
    base_url
        Optional base URL to resolve relative endpoints.
    user_lookup_url_template
        Template URL used to look up a user by subject/username.
    admin_client_id
        Optional client identifier for admin token requests.
    admin_client_secret
        Optional client secret for admin token requests.
    admin_scope
        Optional scope override for admin token requests.
    """

    def __init__(
        self,
        token_url: str,
        userinfo_url: str | None = None,
        introspection_url: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        scope: str | list[str] | None = None,
        verify_tls: bool = True,
        timeout_seconds: int = 10,
        use_basic_auth: bool = True,
        base_url: str | None = None,
        user_lookup_url_template: str | None = None,
        admin_client_id: str | None = None,
        admin_client_secret: str | None = None,
        admin_scope: str | list[str] | None = None,
    ) -> None:
        self._base_url = base_url
        self._token_url = self._build_url(token_url)
        self._userinfo_url = (
            self._build_url(userinfo_url) if userinfo_url else None
        )
        self._introspection_url = (
            self._build_url(introspection_url) if introspection_url else None
        )
        self._user_lookup_url_template = user_lookup_url_template
        self._client_id = client_id
        self._client_secret = client_secret
        self._scope = self._sanitize_scope(scope)
        self._verify_tls = verify_tls
        self._timeout_seconds = timeout_seconds
        self._use_basic_auth = use_basic_auth
        self._admin_client_id = admin_client_id or client_id
        self._admin_client_secret = admin_client_secret or client_secret
        self._admin_scope = self._sanitize_scope(admin_scope) or self._scope

        self._session = requests.Session()

    @property
    def userinfo_url(self) -> str | None:
        """Return the configured userinfo endpoint URL.

        Returns
        -------
            The full userinfo endpoint URL or None.
        """
        return self._userinfo_url

    @property
    def introspection_url(self) -> str | None:
        """Return the configured introspection endpoint URL.

        Returns
        -------
            The full introspection endpoint URL or None.
        """
        return self._introspection_url

    @property
    def user_lookup_url_template(self) -> str | None:
        """Return the configured user lookup URL template.

        Returns
        -------
            URL template for user lookup or None.
        """
        return self._user_lookup_url_template

    def request_password_token(
        self, username: str, password: str
    ) -> dict[str, Any]:
        """Request an access token using the password grant.

        Parameters
        ----------
        username
            Resource owner username.
        password
            Resource owner password.

        Returns
        -------
            Token response payload from the identity provider.
        """
        data: dict[str, Any] = {
            "grant_type": "password",
            "username": username,
            "password": password,
        }
        if self._scope:
            data["scope"] = self._scope
        return self._post_token(data)

    def request_client_credentials_token(self) -> dict[str, Any]:
        """Request an access token using the client credentials grant.

        Returns
        -------
            Token response payload from the identity provider.
        """
        data: dict[str, Any] = {"grant_type": "client_credentials"}
        if self._admin_scope:
            data["scope"] = self._admin_scope
        return self._post_token(data, use_admin=True)

    def get_userinfo(self, access_token: str) -> dict[str, Any]:
        """Fetch user profile information for the given access token.

        Parameters
        ----------
        access_token
            Bearer access token.

        Returns
        -------
            Userinfo response payload.

        Raises
        ------
        exceptions.MissingConfigurationException
            If the userinfo endpoint is not configured.
        """
        if not self._userinfo_url:
            raise exceptions.MissingConfigurationException(
                "userinfo_url is not configured"
            )
        return self._request_json(
            "GET",
            self._userinfo_url,
            headers={"Authorization": f"Bearer {access_token}"},
        )

    def introspect_token(self, token: str) -> dict[str, Any]:
        """Introspect a token using the configured endpoint.

        Parameters
        ----------
        token
            Access or refresh token to introspect.

        Returns
        -------
            Introspection response payload.

        Raises
        ------
        exceptions.MissingConfigurationException
            If the introspection endpoint is not configured.
        """
        if not self._introspection_url:
            raise exceptions.MissingConfigurationException(
                "introspection_url is not configured"
            )
        data = {"token": token}
        return self._request_json(
            "POST",
            self._introspection_url,
            data=data,
            auth=self._build_auth(),
        )

    def get_user_by_subject(self, subject: str) -> dict[str, Any]:
        """Look up a user by subject using the admin client.

        Parameters
        ----------
        subject
            Subject or username to look up.

        Returns
        -------
            User representation returned by the provider.

        Raises
        ------
        exceptions.MissingConfigurationException
            If the user lookup URL template is not configured.
        exceptions.IdentityError
            If an admin token cannot be obtained or response is invalid.
        exceptions.UserNotFoundException
            If the user is not found.
        """
        if not self._user_lookup_url_template:
            raise exceptions.MissingConfigurationException(
                "user_lookup_url_template is not configured"
            )

        token_data = self.request_client_credentials_token()
        access_token = token_data.get("access_token")
        if not access_token:
            raise exceptions.IdentityError(
                "Unable to obtain admin access token"
            )

        url = self._user_lookup_url_template.format(subject=subject)
        response: Any = self._request_json(
            "GET",
            url,
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if isinstance(response, list):
            if not response:
                raise exceptions.UserNotFoundException(
                    f"User '{subject}' not found by identity provider"
                )
            first_item = cast(Mapping[str, Any], response[0])
            return dict(first_item)

        if isinstance(response, Mapping):
            return dict(cast(Mapping[str, Any], response))

        raise exceptions.IdentityError(
            "Unexpected response while fetching user"
        )

    def _post_token(
        self, data: dict[str, Any], use_admin: bool = False
    ) -> dict[str, Any]:
        """Request a token at the token endpoint.

        Parameters
        ----------
        data
            Form payload to send to the token endpoint.
        use_admin, optional
            Whether to use admin client credentials, by default False.

        Returns
        -------
            Token response payload from the identity provider.

        Raises
        ------
        exceptions.MissingConfigurationException
            If the required client identifier is missing.
        """
        if use_admin:
            client_id = self._admin_client_id
            client_secret = self._admin_client_secret
        else:
            client_id = self._client_id
            client_secret = self._client_secret

        if not client_id:
            raise exceptions.MissingConfigurationException(
                "client_id is not configured"
            )

        if not self._token_url:
            raise exceptions.MissingConfigurationException(
                "token_url is not configured"
            )

        if not self._use_basic_auth:
            data["client_id"] = client_id
            if client_secret:
                data["client_secret"] = client_secret

        auth = (
            HTTPBasicAuth(client_id, client_secret)
            if self._use_basic_auth and client_secret
            else None
        )

        return self._request_json(
            method="POST",
            url=self._token_url,
            data=data,
            auth=auth,
        )

    def _request_json(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> Any:
        """Execute an HTTP request and return a JSON response.

        Parameters
        ----------
        method
            HTTP method (GET, POST, etc.).
        url
            Absolute URL for the request.
        **kwargs
            Additional arguments passed to `requests.request()`.

        Returns
        -------
            Parsed JSON response payload.

        Raises
        ------
        exceptions.IdentityError
            If the request fails or returns a non-JSON response.
        exceptions.InvalidCredentialsException
            If the identity provider rejects credentials.
        """
        try:
            response = self._session.request(
                method,
                url,
                timeout=self._timeout_seconds,
                verify=self._verify_tls,
                **kwargs,
            )
        except requests.RequestException as exc:
            raise exceptions.IdentityError(
                f"OAuth2 request failed: {exc}"
            ) from exc

        if response.status_code >= 400:
            message = self._extract_error_message(response)
            if response.status_code in (400, 401, 403):
                raise exceptions.InvalidCredentialsException(message)
            raise exceptions.IdentityError(message)

        try:
            return response.json()
        except ValueError as exc:
            raise exceptions.IdentityError(
                "OAuth2 response did not include JSON payload"
            ) from exc

    @staticmethod
    def _extract_error_message(response: requests.Response) -> str:
        """Extract a provider error message from an HTTP response.

        Parameters
        ----------
        response
            HTTP response returned by the provider.

        Returns
        -------
            Human-readable error message.
        """
        try:
            payload = response.json()
            error = payload.get("error_description") or payload.get("error")
            if error:
                return str(error)
        except ValueError:
            pass
        return f"OAuth2 request failed with status {response.status_code}"

    def _build_url(self, url: str | None) -> str | None:
        """Resolve a relative endpoint against the configured base URL.

        Parameters
        ----------
        url
            Absolute or relative URL.

        Returns
        -------
            Absolute URL when possible, otherwise None.
        """
        if url is None:
            return None
        if self._base_url and not url.startswith("http"):
            return urljoin(self._base_url.rstrip("/") + "/", url)
        return url

    def _build_auth(self) -> HTTPBasicAuth | None:
        """Create HTTP Basic Auth credentials for introspection requests.

        Returns
        -------
            Basic auth instance when configured, otherwise None.
        """
        if not self._client_id or not self._client_secret:
            return None
        if not self._use_basic_auth:
            return None
        return HTTPBasicAuth(self._client_id, self._client_secret)

    def _sanitize_scope(self, scope: str | list[str] | None) -> str | None:
        """Sanitize the scope parameter to be a space-delimited string.

        Parameters
        ----------
        scope
            Scope as a string or list of strings.

        Returns
        -------
            Space-delimited scope string or None.
        """
        if scope is None:
            return None
        if isinstance(scope, list):
            return " ".join(scope)
        return scope


class KeyCloakOIDCConnector(OIDCConnector):
    """Keycloak-specific OIDC connector."""

    def __init__(
        self,
        base_url: str,
        realm: str,
        client_id: str,
        client_secret: str,
        scope: str | list[str] | None = None,
        admin_client_id: str | None = None,
        admin_client_secret: str | None = None,
        admin_scope: str | None = None,
        verify_tls: bool = True,
        timeout_seconds: int = 10,
    ) -> None:
        token_url = (
            f"{base_url}/realms/{realm}" "/protocol/openid-connect/token"
        )
        userinfo_url = (
            f"{base_url}/realms/{realm}" "/protocol/openid-connect/userinfo"
        )
        introspection_url = (
            f"{base_url}/realms/{realm}"
            "/protocol/openid-connect/token/introspect"
        )
        user_lookup_url_template = (
            f"{base_url}/admin/realms/{realm}/users" "?username={subject}"
        )
        super().__init__(
            token_url=token_url,
            userinfo_url=userinfo_url,
            introspection_url=introspection_url,
            client_id=client_id,
            client_secret=client_secret,
            scope=scope,
            verify_tls=verify_tls,
            timeout_seconds=timeout_seconds,
            user_lookup_url_template=user_lookup_url_template,
            admin_client_id=admin_client_id,
            admin_client_secret=admin_client_secret,
            admin_scope=admin_scope,
        )
