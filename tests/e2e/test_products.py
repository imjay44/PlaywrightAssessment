import re
import pytest
from playwright.sync_api import Page, expect
from pages.product_page import ProductPage


@pytest.mark.smoke
@pytest.mark.e2e
def test_e2e_03_listing_open_product_listing(page: Page, product_page: ProductPage):
    """E2E-03: Listing - Open product listing, products show name, image and price."""
    product_page.navigate_listing()
    expect(product_page.catalog_heading).to_contain_text("All products")

    cards = product_page.product_cards
    expect(cards.first).to_be_visible()
    count = cards.count()
    assert count >= 4, f"Expected at least 4 products in catalog, got {count}"

    # Verify each visible product card contains name, price, and image
    for i in range(count):
        card = cards.nth(i)
        expect(card.locator("img")).to_be_visible()
        card_text = card.inner_text()
        assert "$" in card_text, f"Product card {i} does not display price: {card_text}"
        assert len(card_text.strip()) > 3, f"Product card {i} does not display name: {card_text}"


@pytest.mark.e2e
def test_e2e_04_search_known_product(page: Page, product_page: ProductPage):
    """E2E-04: Search - Search for a known product, only matching products appear."""
    product_page.search_via_url("chair")
    cards = product_page.product_cards
    expect(cards.first).to_be_visible()
    
    count = cards.count()
    assert count > 0, "Expected at least one result for search 'chair'"
    for i in range(count):
        card_text = cards.nth(i).inner_text().lower()
        assert "chair" in card_text, f"Product card {i} does not match search term 'chair': {card_text}"


@pytest.mark.e2e
def test_e2e_05_search_nonsense_term(page: Page, product_page: ProductPage):
    """E2E-05: Search - Search for a nonsense term, 'No results' message shown."""
    product_page.search_via_url("nonsensexyz987654")
    expect(product_page.no_results_message).to_be_visible()
    expect(product_page.product_cards).to_have_count(0)


@pytest.mark.e2e
def test_e2e_06_sort_price_low_to_high(page: Page, product_page: ProductPage):
    """E2E-06: Filter/Sort - Sort by price low to high, prices are in ascending order."""
    product_page.navigate_listing()
    product_page.sort_by_price_low_to_high()
    
    prices = product_page.get_product_card_prices()
    assert len(prices) >= 2, f"Need at least 2 prices to verify sorting, found {prices}"
    assert prices == sorted(prices), f"Prices are not in ascending order: {prices}"


@pytest.mark.smoke
@pytest.mark.e2e
def test_e2e_07_product_detail_page(page: Page, product_page: ProductPage):
    """E2E-07: Product detail - Open a product, name, price, description and add-to-cart are shown."""
    product_page.open_product("linen-lounge-chair")
    
    expect(product_page.product_detail_title).to_contain_text("Linen lounge chair")
    expect(product_page.product_detail_price).to_contain_text("$640.00")
    expect(product_page.product_detail_description).to_be_visible()
    expect(product_page.add_to_cart_btn).to_be_visible()
    expect(product_page.add_to_cart_btn).to_be_enabled()

