import re
from typing import Dict, List, Optional
from playwright.sync_api import Page, Locator, expect


class CheckoutPage:
    """Page Object for Northline Store Checkout flow."""

    def __init__(self, page: Page):
        self.page = page
        self.checkout_heading: Locator = page.locator("h1:has-text('Checkout')")
        self.empty_cart_message: Locator = page.get_by_text("Your cart is empty.")
        
        # Step 1: Address Form inputs
        self.line1_input: Locator = page.get_by_label("Address")
        self.line2_input: Locator = page.get_by_label("Apartment, suite (optional)")
        self.city_input: Locator = page.get_by_label("City")
        self.state_input: Locator = page.get_by_label("State")
        self.postal_code_input: Locator = page.get_by_label("Postal code")
        self.country_input: Locator = page.get_by_label("Country")
        self.phone_input: Locator = page.get_by_label("Phone (optional)")
        self.continue_to_review_btn: Locator = page.get_by_role("button", name="Continue to review")
        
        # Step 2: Review & Place Order
        self.review_info_text: Locator = page.get_by_text("Card checkout is not enabled")
        self.shipping_to_box: Locator = page.locator("div:has(> p:text-is('Shipping to'))")
        self.place_order_btn: Locator = page.get_by_role("button", name=re.compile(r"Place order"))
        self.back_button: Locator = page.get_by_role("button", name="Back")
        
        # Confirmation
        self.order_confirmed_badge: Locator = page.get_by_text("Order confirmed")
        self.thank_you_heading: Locator = page.locator("h1:has-text('Thank you')")
        self.order_status_paragraph: Locator = page.locator("p:has-text('is paid')")
        
        # Error messages
        self.error_messages: Locator = page.locator(".text-danger-600, [class*='text-danger']")

    def navigate(self):
        """Navigate to checkout page."""
        self.page.goto("/checkout")
        self.page.wait_for_load_state("networkidle")

    def fill_address(self, data: Dict[str, str]):
        """Fill address form with provided dictionary."""
        if "line1" in data:
            self.line1_input.fill(data["line1"])
        if "line2" in data and data["line2"]:
            self.line2_input.fill(data["line2"])
        if "city" in data:
            self.city_input.fill(data["city"])
        if "state" in data and data["state"]:
            self.state_input.fill(data["state"])
        if "postalCode" in data:
            self.postal_code_input.fill(data["postalCode"])
        if "country" in data:
            self.country_input.fill(data["country"])
        if "phone" in data and data["phone"]:
            self.phone_input.fill(data["phone"])

    def submit_address(self):
        """Submit the shipping address step."""
        self.continue_to_review_btn.click()
        self.page.wait_for_timeout(500)

    def place_order(self):
        """Click the Place order button on the review step."""
        self.place_order_btn.click()
        self.page.wait_for_load_state("networkidle")

    def get_validation_errors(self) -> List[str]:
        """Return list of visible validation error texts."""
        return [err.inner_text().strip() for err in self.error_messages.all() if err.is_visible()]

