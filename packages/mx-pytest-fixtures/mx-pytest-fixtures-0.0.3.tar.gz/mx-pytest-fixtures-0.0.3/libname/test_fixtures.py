import pytest

@pytest.fixture(scope="session")
def auth_header():
    auth_key = "RandomPhrase123"
    return {'AuthKey': auth_key}
