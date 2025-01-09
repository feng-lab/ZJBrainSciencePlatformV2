import asyncio
from test import login

import pytest
from app.common.config import config
import alembic.command
import alembic.config
from app.api import encrypt_password
from app.api.user import ROOT_PASSWORD, ROOT_USERNAME
from app.main import app

@pytest.fixture(scope="session")
def run_app_startup_shutdown() -> None:
    asyncio.run(app.router.startup())
    yield
    asyncio.run(app.router.shutdown())


@pytest.fixture(scope="session")
def run_alembic_upgrade_head() -> None:
    alembic_config = alembic.config.Config("alembic.ini")
    alembic.command.upgrade(alembic_config, "head")


@pytest.fixture(scope="session")
def logon_root_headers(request,run_alembic_upgrade_head, run_app_startup_shutdown) -> dict[str, str]:

    if config.ENABLE_KEYCLOAK :
        return login(ROOT_USERNAME, encrypt_password(ROOT_PASSWORD))
    elif config.ENABLE_KEYCLOAK:
        return login("data-management", "0p9jizKBOrahVzZKzhgW")
