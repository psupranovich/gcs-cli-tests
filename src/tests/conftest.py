import pytest
from playwright.sync_api import Playwright, sync_playwright

from src.gcp_test_client.gcp_client import GcpStorage

DEFAULT_TIMEOUT_MS = 30000


pytest_plugins = [
    'src.fixtures.gsp_fixture',
]


@pytest.fixture(scope="session")
def pw():
    p = sync_playwright().start()
    yield p
    p.stop()


@pytest.fixture(scope="session")
def browser(pw: Playwright):
    browser = pw.chromium.launch(
        headless=False,
        args=["--disable-web-security"],
    )
    yield browser
    browser.close()


@pytest.fixture()
def context(browser):
    context = browser.new_context(ignore_https_errors=True)
    context.set_default_timeout(DEFAULT_TIMEOUT_MS)
    yield context
    context.close()


@pytest.fixture()
def page(context):
    page = context.new_page()
    yield page
    page.close()


@pytest.fixture(scope="session")
def gcp_client():
    return GcpStorage()


