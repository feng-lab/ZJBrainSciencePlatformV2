import asyncio
from test import login

import pytest

import alembic.command
import alembic.config
from app.api import encrypt_password
from app.api.user import ROOT_PASSWORD, ROOT_USERNAME
from app.main import app

def pytest_addoption(parser):
    parser.addoption(
        "--test-mode",
        action="store",
        default="current",
        help="选择测试模式：'current'（当前代码）或 'legacy'（之前代码）",
    )

# 获取 config 变量
@pytest.fixture(scope="session")
def config(request):
    return request.config.getoption("--test-mode")

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
    config = request.config.getoption("--test-mode")
    if config =="legacy":
        return login(ROOT_USERNAME, encrypt_password(ROOT_PASSWORD),config)
    elif config =="current":
        return login("admin", "admin",config)
