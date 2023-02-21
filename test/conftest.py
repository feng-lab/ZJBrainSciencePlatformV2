from test import login

import pytest

from app.api.user import ROOT_PASSWORD, ROOT_USERNAME


@pytest.fixture(scope="session")
def logon_root_headers() -> dict[str, str]:
    return login(ROOT_USERNAME, ROOT_PASSWORD)
