import re
import pytest
from playwright.sync_api import Page, expect
from pages.product_page import ProductPage
from pages.cart_page import CartPage


@pytest.mark.smoke
@pytest.mark.e2e
def test_e2e_08_add_item_to_cart(page: Page, product_page: ProductPage, cart_page: CartPage):
    """E2E-08: Cart - Add item to cart, cart count increases, item appears in cart."""
    product_page.open_product("linen-lounge-chair")
    product_page.add_to_cart()

    # Verify cart header button shows count
    cart_btn = page.locator("header").get_by_role("button", name=re.compile(r"Cart"))
    expect(cart_btn).to_contain_text("Cart (1)")

    # Navigate to Cart page and verify item is present
    cart_page.navigate()
    expect(cart_page.cart_heading).to_be_visible()
    expect(page.get_by_text("Linen lounge chair").first).to_be_visible()
    expect(cart_page.order_summary_heading).to_be_visible()


@pytest.mark.e2e
def test_e2e_09_change_quantity_updates_totals(page: Page, product_page: ProductPage, cart_page: CartPage):
    """E2E-09: Cart - Change quantity, line total and subtotal update correctly."""
    product_page.open_product("ceramic-pour-over-set")
    product_page.add_to_cart()

    cart_page.navigate()
    initial_subtotal = cart_page.get_subtotal_amount()
    assert initial_subtotal == 86.00

    # Increase quantity by 1
    cart_page.increase_quantity(0)
    page.wait_for_timeout(500)

    # Subtotal should double (86 * 2 = 172.00)
    new_subtotal = cart_page.get_subtotal_amount()
    assert new_subtotal == 172.00, f"Expected subtotal 172.00, got {new_subtotal}"

    # Decrease quantity back to 1
    cart_page.decrease_quantity(0)
    page.wait_for_timeout(500)
    assert cart_page.get_subtotal_amount() == 86.00


@pytest.mark.e2e
def test_e2e_10_remove_item_recalculates_totals(page: Page, product_page: ProductPage, cart_page: CartPage):
    """E2E-10: Cart - Remove item, item is removed from cart list and item count updates."""
    # Add two different items
    product_page.open_product("ceramic-pour-over-set")
    product_page.add_to_cart()

    product_page.open_product("wool-throw-blanket")
    product_page.add_to_cart()

    cart_page.navigate()
    expect(cart_page.remove_buttons).to_have_count(2)

    # Remove the first item
    cart_page.remove_item(0)
    page.wait_for_timeout(500)

    # Verify item is removed and cart item list has 1 item remaining
    expect(cart_page.remove_buttons).to_have_count(1)


@pytest.mark.e2e
def test_e2e_11_empty_cart_shows_empty_state(page: Page, product_page: ProductPage, cart_page: CartPage):
    """E2E-11: Cart - Empty cart, empty-state message shown."""
    product_page.open_product("wool-throw-blanket")
    product_page.add_to_cart()

    cart_page.navigate()
    expect(cart_page.remove_buttons.first).to_be_visible()
    cart_page.remove_item(0)

    expect(cart_page.empty_cart_message).to_be_visible()
    expect(cart_page.continue_shopping_link).to_be_visible()


@pytest.mark.e2e
def test_e2e_12_shipping_charge_applied_below_threshold(page: Page, cart_page: CartPage):
    """E2E-12: Shipping - Subtotal below $75, shipping charge is applied ($9.99)."""
    # Intercept catalog to provide an item under $75 threshold
    def provide_low_cost_product(route):
        response = route.fetch()
        data = response.json()
        data["products"].append({
            "id": "prod-linen-coaster",
            "name": "Linen Coaster Set",
            "slug": "linen-coaster-set",
            "description": "Minimalist linen coaster set.",
            "price": "35.00",
            "stockQuantity": 20,
            "sku": "NL-OBJ-035",
            "images": ["https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=600&q=80"],
            "categoryId": "cat-objects",
            "isActive": True,
            "createdAt": "2026-09-01T10:00:00.000Z",
            "category": {"id": "cat-objects", "name": "Objects", "slug": "objects"}
        })
        route.fulfill(json=data)

    page.route("**/catalog.json", provide_low_cost_product)
    page.goto("/products/linen-coaster-set")
    page.wait_for_load_state("networkidle")

    page.get_by_role("button", name="Add to cart").click()
    page.wait_for_timeout(500)

    cart_page.navigate()
    assert cart_page.get_subtotal_amount() < 75.00
    shipping_text = cart_page.get_shipping_text()
    assert shipping_text == "$9.99", f"Expected $9.99 shipping charge below $75, got {shipping_text}"


@pytest.mark.e2e
def test_e2e_13_shipping_shows_free_above_threshold(page: Page, product_page: ProductPage, cart_page: CartPage):
    """E2E-13: Shipping - Subtotal above $75, shipping shows as free."""
    product_page.open_product("ceramic-pour-over-set")  # $86.00 > $75.00
    product_page.add_to_cart()

    cart_page.navigate()
    assert cart_page.get_subtotal_amount() >= 75.00
    shipping_text = cart_page.get_shipping_text()
    assert shipping_text.lower() == "free", f"Expected 'Free' shipping above $75, got {shipping_text}"


@pytest.mark.e2e
def test_e2e_17_persistence_reload_with_items_in_cart(page: Page, product_page: ProductPage, cart_page: CartPage):
    """E2E-17: Persistence - Reload page with items in cart, cart contents preserved."""
    product_page.open_product("linen-lounge-chair")
    product_page.add_to_cart()

    cart_page.navigate()
    expect(page.get_by_text("Linen lounge chair").first).to_be_visible()
    initial_subtotal = cart_page.get_subtotal_amount()

    # Reload page
    page.reload()
    page.wait_for_load_state("networkidle")

    # Verify cart contents preserved
    expect(page.get_by_text("Linen lounge chair").first).to_be_visible()
    assert cart_page.get_subtotal_amount() == initial_subtotal

