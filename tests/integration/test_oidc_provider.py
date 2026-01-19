import os
import pytest
from alpha.providers.models.identity import Identity


@pytest.mark.skipif(
    os.getenv("GITHUB_ACTIONS") == "true",
    reason="Unable to run KeyCloak service in GitHub Actions",
)
def test_keycloak_provider_authenticate(
    keycloak_provider, keycloak_credentials
):

    result = keycloak_provider.authenticate(keycloak_credentials)

    assert isinstance(result, Identity)
    assert result.username == "alice"
    assert result.display_name == "Alice Tester"
    assert result.email == "alice@example.com"
    assert result.groups == []
    assert result.claims.get("token_type") == "Bearer"
