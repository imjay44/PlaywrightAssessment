import re
import pytest
from playwright.sync_api import Page, expect
from pages.home_page import HomePage
from pages.product_page import ProductPage
from pages.cart_page import CartPage


@pytest.mark.e2e
def test_e2e_18_responsive_mobile_viewport_key_flow(mobile_page: Page):
    """E2E-18: Responsive - Run key flow at 390x844, layout usable, navigation and cart work on mobile."""
    # 1. Verify viewport is 390x844
    viewport = mobile_page.viewport_size
    assert viewport["width"] == 390
    assert viewport["height"] == 844

    # 2. Load Home on mobile
    home_p = HomePage(mobile_page)
    home_p.navigate()
    expect(home_p.header).to_be_visible()
    expect(mobile_page.get_by_role("link", name="Northline")).to_be_visible()

    # 3. Navigate to product detail on mobile
    prod_p = ProductPage(mobile_page)
    prod_p.open_product("linen-lounge-chair")
    expect(prod_p.product_detail_title).to_be_visible()
    expect(prod_p.add_to_cart_btn).to_be_visible()

    # 4. Add to cart on mobile
    prod_p.add_to_cart()

    # 5. Open Cart on mobile
    cart_p = CartPage(mobile_page)
    cart_p.navigate()
    expect(cart_p.cart_heading).to_be_visible()
    expect(mobile_page.get_by_text("Linen lounge chair").first).to_be_visible()
    expect(cart_p.order_summary_heading).to_be_visible()
    expect(cart_p.checkout_link).to_be_visible()


@pytest.mark.smoke
@pytest.mark.e2e
def test_e2e_19_cross_browser_smoke_check(page: Page, home_page: HomePage, product_page: ProductPage):
    """E2E-19: Cross-browser - Run smoke test to verify essential journey passes across browser engines."""
    home_page.navigate()
    expect(page).to_have_title(re.compile(r"Northline"))

    product_page.navigate_listing()
    expect(product_page.product_cards.first).to_be_visible()

    product_page.open_product("wool-throw-blanket")
    expect(product_page.product_detail_title).to_contain_text("Wool throw blanket")
    expect(product_page.add_to_cart_btn).to_be_enabled()

