from requests.auth import HTTPBasicAuth

from alpha.infra.connectors.oidc_connector import OIDCConnector


def test_oidc_connector(oidc_connector):

    assert oidc_connector._base_url == "https://example.com"
    assert oidc_connector._token_url == "https://example.com/token"
    assert oidc_connector._userinfo_url is None
    assert (
        oidc_connector._introspection_url == "https://example.com/introspect"
    )
    assert oidc_connector._client_id == "fake_client_id"
    assert oidc_connector._client_secret == "fake_client_secret"
    assert oidc_connector._scope == "openid profile email"

    assert oidc_connector.userinfo_url is None
    assert oidc_connector.introspection_url == "https://example.com/introspect"
    assert oidc_connector.user_lookup_url_template == "test/users/{user_id}"


def test_oidc_connector_extract_error_message(fake_reponse):

    assert (
        OIDCConnector._extract_error_message(
            fake_reponse(
                400,
                {
                    "error": "invalid_request",
                    "error_description": "Bad request",
                },
            )
        )
        == "Bad request"
    )
    assert (
        OIDCConnector._extract_error_message(
            fake_reponse(
                400,
                {
                    "error": "invalid_request",
                },
            )
        )
        == "invalid_request"
    )
    assert (
        OIDCConnector._extract_error_message(
            fake_reponse(
                400,
                {},
            )
        )
        == "OAuth2 request failed with status 400"
    )


def test_oidc_connector_build_url(oidc_connector):

    url = oidc_connector._build_url("endpoint/path")
    assert url == "https://example.com/endpoint/path"


def test_oidc_connector_build_auth(oidc_connector):
    auth = oidc_connector._build_auth()

    assert isinstance(auth, HTTPBasicAuth)
    assert auth.username == "fake_client_id"
    assert auth.password == "fake_client_secret"


def test_oidc_connector_sanitize_scope(oidc_connector):
    scope = oidc_connector._sanitize_scope(["openid", "profile", "email"])
    assert scope == "openid profile email"
