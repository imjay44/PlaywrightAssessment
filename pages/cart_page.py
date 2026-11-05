import re
from typing import Optional
from playwright.sync_api import Page, Locator, expect


class CartPage:
    """Page Object for Northline Store Cart page and Drawer."""

    def __init__(self, page: Page):
        self.page = page
        self.cart_heading: Locator = page.locator("h1:has-text('Cart')")
        self.empty_cart_message: Locator = page.get_by_text("Your cart is empty.")
        self.continue_shopping_link: Locator = page.get_by_role("link", name="Continue shopping")
        
        # Summary & items
        self.order_summary_heading: Locator = page.locator("h2:has-text('Order summary')")
        self.checkout_link: Locator = page.get_by_role("link", name="Checkout")
        self.remove_buttons: Locator = page.get_by_role("button", name="Remove")
        self.increase_qty_buttons: Locator = page.get_by_role("button", name="Increase quantity")
        self.decrease_qty_buttons: Locator = page.get_by_role("button", name="Decrease quantity")
        
        # Free shipping threshold note
        self.free_shipping_notice: Locator = page.locator("p:has-text('Free shipping over')")
        self.promo_input: Locator = page.locator("input[placeholder='Promo code']")
        self.apply_promo_btn: Locator = page.get_by_role("button", name="Apply")

    def navigate(self):
        """Navigate to cart page."""
        self.page.goto("/cart")
        self.page.wait_for_load_state("networkidle")

    def get_subtotal_text(self) -> str:
        loc = self.page.locator("div:has(> dt:text-is('Subtotal')) > dd")
        return loc.inner_text().strip()

    def get_subtotal_amount(self) -> float:
        text = self.get_subtotal_text()
        return float(text.replace("$", "").replace(",", ""))

    def get_shipping_text(self) -> str:
        loc = self.page.locator("div:has(> dt:text-is('Shipping')) > dd")
        return loc.inner_text().strip()

    def get_total_amount(self) -> float:
        loc = self.page.locator("div:has(> dt:text-is('Total')) > dd")
        text = loc.inner_text().strip()
        return float(text.replace("$", "").replace(",", ""))

    def increase_quantity(self, index: int = 0):
        self.increase_qty_buttons.nth(index).click()
        self.page.wait_for_timeout(300)

    def decrease_quantity(self, index: int = 0):
        self.decrease_qty_buttons.nth(index).click()
        self.page.wait_for_timeout(300)

    def remove_item(self, index: int = 0):
        self.remove_buttons.nth(index).click()
        self.page.wait_for_timeout(300)

    def click_checkout(self):
        self.checkout_link.click()
        self.page.wait_for_load_state("networkidle")

