import re
from typing import List
from playwright.sync_api import Page, Locator, expect


class ProductPage:
    """Page Object for Northline Store Product Listing and Product Detail pages."""

    def __init__(self, page: Page):
        self.page = page
        
        # Product Listing elements
        self.catalog_heading: Locator = page.locator("h1")
        self.product_cards: Locator = page.locator("a[href^='/products/']")
        self.sort_button: Locator = page.get_by_role("button", name=re.compile(r"Newest|Price:|Popularity"))
        self.no_results_message: Locator = page.get_by_text("No products match these filters.")
        self.clear_filters_btn: Locator = page.get_by_role("button", name="Clear filters")
        
        # Product Detail elements
        self.product_detail_title: Locator = page.locator("h1")
        self.product_detail_price: Locator = page.locator("main p.text-2xl.font-semibold")
        self.product_detail_description: Locator = page.locator("main p.leading-6").first
        self.add_to_cart_btn: Locator = page.get_by_role("button", name="Add to cart")
        self.buy_now_btn: Locator = page.get_by_role("button", name="Buy now")
        self.quantity_display: Locator = page.locator("span.min-w-8")
        self.increase_qty_btn: Locator = page.get_by_role("button", name="Increase quantity")
        self.decrease_qty_btn: Locator = page.get_by_role("button", name="Decrease quantity")
        self.stock_badge: Locator = page.locator("span:has-text('stock'), span:has-text('left')").first
        self.related_products_section: Locator = page.locator("section:has-text('Related products')")

    def navigate_listing(self):
        """Navigate to the /products catalog page."""
        self.page.goto("/products")
        self.page.wait_for_load_state("networkidle")

    def search_via_url(self, query: str):
        """Perform search by navigating to products with search query parameter."""
        self.page.goto(f"/products?search={query}")
        self.page.wait_for_load_state("networkidle")

    def sort_by_price_low_to_high(self):
        """Click sort dropdown and select Price: low to high."""
        self.sort_button.click()
        self.page.get_by_text("Price: low to high").click()
        self.page.wait_for_url(re.compile(r"sortId=price-asc"))
        self.page.wait_for_load_state("networkidle")
        # Auto-wait for the first product to be the lowest priced item ($86.00)
        expect(self.product_cards.first).to_contain_text("$86.00")

    def get_product_card_names(self) -> List[str]:
        """Return inner text of all product cards in listing."""
        expect(self.product_cards.first).to_be_visible()
        cards = self.product_cards.all()
        return [card.inner_text() for card in cards]

    def get_product_card_prices(self) -> List[float]:
        """Extract prices from product cards as float values."""
        texts = self.get_product_card_names()
        prices = []
        for text in texts:
            # find all dollar prices in card (take the last one which is current selling price)
            matches = re.findall(r"\$([0-9]+(?:\.[0-9]{2})?)", text)
            if matches:
                prices.append(float(matches[-1]))
        return prices

    def open_product(self, slug: str):
        """Navigate to product detail page directly."""
        self.page.goto(f"/products/{slug}")
        self.page.wait_for_load_state("networkidle")

    def click_first_product(self):
        """Click the first product card on the listing page."""
        first_card = self.product_cards.first
        first_card.click()
        self.page.wait_for_load_state("networkidle")

    def add_to_cart(self):
        """Click Add to cart button."""
        self.add_to_cart_btn.click()
        # Toast or drawer trigger animation auto-waited
        self.page.wait_for_timeout(500)

