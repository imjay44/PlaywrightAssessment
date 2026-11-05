import json
import os
from typing import Generator
import pytest
from playwright.sync_api import Page, Browser, BrowserContext, APIRequestContext, Playwright
from pages.home_page import HomePage
from pages.product_page import ProductPage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.environ.get("BASE_URL", "https://ecomcicid.netlify.app")


@pytest.fixture
def home_page(page: Page) -> HomePage:
    return HomePage(page)


@pytest.fixture
def product_page(page: Page) -> ProductPage:
    return ProductPage(page)


@pytest.fixture
def cart_page(page: Page) -> CartPage:
    return CartPage(page)


@pytest.fixture
def checkout_page(page: Page) -> CheckoutPage:
    return CheckoutPage(page)


@pytest.fixture
def mobile_context(browser: Browser, base_url: str) -> Generator[BrowserContext, None, None]:
    """Browser context configured for mobile viewport 390x844."""
    context = browser.new_context(
        base_url=base_url,
        viewport={"width": 390, "height": 844},
        user_agent=(
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
        ),
        is_mobile=True,
        has_touch=True
    )
    yield context
    context.close()


@pytest.fixture
def mobile_page(mobile_context: BrowserContext) -> Generator[Page, None, None]:
    page = mobile_context.new_page()
    yield page
    page.close()


@pytest.fixture
def api_request_context(playwright: Playwright, base_url: str) -> Generator[APIRequestContext, None, None]:
    """APIRequestContext configured with base URL."""
    context = playwright.request.new_context(base_url=base_url)
    yield context
    context.dispose()


@pytest.fixture
def catalog_schema() -> dict:
    schema_path = os.path.join(os.path.dirname(__file__), "data", "catalog_schema.json")
    with open(schema_path, "r") as f:
        return json.load(f)


@pytest.fixture
def product_schema() -> dict:
    schema_path = os.path.join(os.path.dirname(__file__), "data", "product_schema.json")
    with open(schema_path, "r") as f:
        return json.load(f)


@pytest.fixture
def checkout_fixtures() -> dict:
    fixture_path = os.path.join(os.path.dirname(__file__), "data", "checkout_data.json")
    with open(fixture_path, "r") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def electronic_api_url() -> str:
    """MockAPI endpoint provided for electronic products API."""
    return os.environ.get("ELECTRONIC_API_URL", "https://681444af225ff1af16285b31.mockapi.io/electronicapi")


@pytest.fixture
def electronic_api_context(playwright: Playwright) -> Generator[APIRequestContext, None, None]:
    """APIRequestContext configured for the MockAPI endpoint."""
    context = playwright.request.new_context(base_url="https://681444af225ff1af16285b31.mockapi.io")
    yield context
    context.dispose()


@pytest.fixture
def electronic_api_schema() -> dict:
    schema_path = os.path.join(os.path.dirname(__file__), "data", "electronic_api_schema.json")
    with open(schema_path, "r") as f:
        return json.load(f)

