import re
from playwright.sync_api import Page, Locator, expect


class HomePage:
    """Page Object for Northline Store Home page."""

    def __init__(self, page: Page):
        self.page = page
        self.header: Locator = page.locator("header")
        self.navigation: Locator = page.get_by_role("navigation")
        self.footer: Locator = page.get_by_role("contentinfo")
        self.brand_link: Locator = page.locator("header").get_by_role("link", name="Northline")
        self.products_nav_link: Locator = page.locator("header").get_by_role("link", name="Products")
        self.cart_header_button: Locator = page.locator("header").get_by_role("button", name=re.compile(r"^Cart"))
        self.sign_in_link: Locator = page.locator("header").get_by_role("link", name="Sign in")
        self.hero_heading: Locator = page.locator("h1")
        self.shop_collection_btn: Locator = page.get_by_role("link", name="Shop the collection")
        self.view_new_arrivals_btn: Locator = page.get_by_role("link", name="View new arrivals")
        self.featured_section: Locator = page.locator("section:has-text('Featured pieces')")
        self.categories_section: Locator = page.locator("section:has-text('Categories')")

    def navigate(self):
        """Navigate to home page and wait for network load."""
        self.page.goto("/")
        self.page.wait_for_load_state("networkidle")

    def click_products_menu(self):
        self.products_nav_link.click()
        self.page.wait_for_load_state("networkidle")

    def click_cart(self):
        self.cart_header_button.click()

    def get_cart_count_text(self) -> str:
        return self.cart_header_button.inner_text()
