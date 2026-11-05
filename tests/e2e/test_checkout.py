import re
import pytest
from playwright.sync_api import Page, expect
from pages.product_page import ProductPage
from pages.checkout_page import CheckoutPage


@pytest.fixture
def prep_cart_with_item(page: Page, product_page: ProductPage):
    """Helper to ensure cart has at least one item before heading to checkout."""
    product_page.open_product("ceramic-pour-over-set")
    product_page.add_to_cart()


@pytest.mark.e2e
def test_e2e_14_checkout_submit_empty_fields_shows_validation_errors(
    page: Page, prep_cart_with_item, checkout_page: CheckoutPage
):
    """E2E-14: Checkout - Submit with empty fields, validation errors shown for required fields."""
    checkout_page.navigate()
    expect(checkout_page.checkout_heading).to_be_visible()

    # Clear pre-filled fields if any and click continue
    checkout_page.country_input.fill("")
    checkout_page.submit_address()

    # Assert required field error messages appear
    errors = checkout_page.get_validation_errors()
    assert any("address" in err.lower() for err in errors), f"Address error missing: {errors}"
    assert any("city" in err.lower() for err in errors), f"City error missing: {errors}"
    assert any("postal code" in err.lower() for err in errors), f"Postal code error missing: {errors}"


@pytest.mark.e2e
def test_e2e_15_checkout_invalid_postcode_and_country_shows_field_errors(
    page: Page, prep_cart_with_item, checkout_page: CheckoutPage
):
    """E2E-15: Checkout - Invalid country code / short postcode shows field-level error."""
    checkout_page.navigate()

    # Fill valid address & city, but invalid country length (e.g. 3 characters) & short postal code
    checkout_page.fill_address({
        "line1": "100 Broadway",
        "city": "New York",
        "postalCode": "1",    # minimum 2 characters required by schema
        "country": "USA"      # must be exactly 2-letter ISO code
    })
    checkout_page.submit_address()

    errors = checkout_page.get_validation_errors()
    assert any("2-letter" in err.lower() or "country" in err.lower() for err in errors), (
        f"Country error missing: {errors}"
    )


@pytest.mark.smoke
@pytest.mark.e2e
def test_e2e_16_checkout_valid_details_reaches_order_confirmation(
    page: Page, prep_cart_with_item, checkout_page: CheckoutPage, checkout_fixtures: dict
):
    """E2E-16: Checkout - Valid details, order confirmation page shown."""
    checkout_page.navigate()

    # 1. Fill valid address from fixture
    valid_data = checkout_fixtures["valid_address"]
    checkout_page.fill_address(valid_data)
    checkout_page.submit_address()

    # 2. Verify review step is displayed
    expect(checkout_page.review_info_text).to_be_visible()
    expect(checkout_page.place_order_btn).to_be_visible()

    # 3. Complete order
    checkout_page.place_order()

    # 4. Assert URL and confirmation screen elements
    expect(page).to_have_url(re.compile(r"/orders/.+/confirmed"))
    expect(checkout_page.thank_you_heading).to_be_visible()
    expect(checkout_page.order_confirmed_badge).to_be_visible()
    expect(page.get_by_role("link", name="Keep shopping")).to_be_visible()

