import asyncio
from test import login

import pytest

from app.api.user import ROOT_PASSWORD, ROOT_USERNAME
from app.main import app


@pytest.fixture(scope="session")
def run_app_startup_shutdown() -> None:
    asyncio.run(app.router.startup())
    yield
    asyncio.run(app.router.shutdown())


@pytest.fixture(scope="session")
def logon_root_headers(run_app_startup_shutdown) -> dict[str, str]:
    return login(ROOT_USERNAME, ROOT_PASSWORD)
