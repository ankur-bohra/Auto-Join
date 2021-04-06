import pytest

from src import calendar_api

# Credentials
@pytest.fixture
def scopes():
    return ["https://www.googleapis.com/auth/calendar.readonly", "https://www.googleapis.com/auth/calendar.events.readonly"]

class TestAuthFlow:
    def test_get_creds_without_folder(self, scopes):
        credentials = calendar_api.get_creds(scopes, reuse_creds=False)
        assert credentials.valid

    def test_get_creds_with_folder(self, scopes):
        credentials = calendar_api.get_creds(scopes, "data", reuse_creds=False)
        assert credentials.valid

    def test_get_creds_from_auth_file(self, scopes):
        credentials = calendar_api.get_creds(scopes)
        assert credentials.valid

    def test_get_creds_without_auth_prompt(self, scopes, capsys):
        credentials = calendar_api.get_creds(scopes, reuse_creds=False, show_auth_prompt=False)
        output = capsys.readouterr()
        assert output.out == "\n"