import re
import pytest
from playwright.sync_api import Page, expect
from pages.home_page import HomePage


@pytest.mark.smoke
@pytest.mark.e2e
def test_e2e_01_home_page_loads(page: Page, home_page: HomePage):
    """E2E-01: Page loads - Title contains Northline, header, navigation and footer are visible."""
    home_page.navigate()
    expect(page).to_have_title(re.compile(r"Northline"))
    expect(home_page.header).to_be_visible()
    expect(home_page.navigation).to_be_visible()
    expect(home_page.footer).to_be_visible()
    expect(home_page.hero_heading).to_be_visible()


@pytest.mark.smoke
@pytest.mark.e2e
def test_e2e_02_navigation_click_main_menu_items(page: Page, home_page: HomePage):
    """E2E-02: Navigation - Click each main menu item, correct page loads, no console errors."""
    console_errors = []
    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

    # 1. Start at Home
    home_page.navigate()
    expect(page).to_have_title(re.compile(r"Northline"))

    # 2. Click 'Products' in navigation
    home_page.click_products_menu()
    expect(page).to_have_url(re.compile(r"/products"))
    expect(page.get_by_role("heading", level=1)).to_contain_text("All products")

    # 3. Click 'Northline' brand link to return home
    home_page.brand_link.click()
    page.wait_for_load_state("networkidle")
    expect(page).to_have_url(re.compile(r"/$"))

    # 4. Click 'Sign in' link in navigation
    home_page.sign_in_link.click()
    page.wait_for_load_state("networkidle")
    expect(page).to_have_url(re.compile(r"/login"))
    expect(page.get_by_role("heading", level=1)).to_contain_text("Welcome back")
    expect(page.get_by_role("button", name="Sign in")).to_be_visible()

    # 5. Verify no uncaught console errors occurred during navigation
    # Filter out known external network warnings if any
    critical_errors = [err for err in console_errors if "favicon" not in err.lower()]
    assert len(critical_errors) == 0, f"Encountered unexpected console errors: {critical_errors}"


@pytest.mark.e2e
def test_e2e_20_negative_open_invalid_url(page: Page):
    """E2E-20: Negative - Open an invalid URL shows friendly unavailable state or link back to catalog."""
    page.goto("/products/non-existent-product-item-xyz")
    page.wait_for_load_state("networkidle")

    # Check for friendly error message and back to catalog navigation
    expect(page.get_by_role("heading", level=1)).to_contain_text("Product unavailable")
    expect(page.get_by_text("The store API is not connected on this host.")).to_be_visible()

    back_link = page.get_by_role("link", name="Back to catalog")
    expect(back_link).to_be_visible()
    back_link.click()
    page.wait_for_load_state("networkidle")
    expect(page).to_have_url(re.compile(r"/products"))
