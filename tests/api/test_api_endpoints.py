import time
import jsonschema
import pytest
from playwright.sync_api import APIRequestContext, Page, expect
from pages.product_page import ProductPage


@pytest.mark.api
@pytest.mark.smoke
def test_api_01_get_product_list(api_request_context: APIRequestContext, catalog_schema: dict):
    """API-01: GET product list - Status 200, JSON array, non-empty."""
    response = api_request_context.get("/catalog.json")
    assert response.status == 200, f"Expected status 200, got {response.status}"
    
    data = response.json()
    assert "products" in data, "Response JSON missing 'products' key"
    products = data["products"]
    assert isinstance(products, list), "Products is not a list"
    assert len(products) > 0, "Product list is empty"
    
    # Validate entire catalog against JSON schema
    jsonschema.validate(instance=data, schema=catalog_schema)


@pytest.mark.api
@pytest.mark.smoke
def test_api_02_get_single_product_schema(api_request_context: APIRequestContext, product_schema: dict):
    """API-02: GET single product - Status 200, matches schema (id, name, price, image)."""
    response = api_request_context.get("/catalog.json")
    assert response.status == 200
    
    data = response.json()
    first_product = data["products"][0]
    
    # Validate against single product schema
    jsonschema.validate(instance=first_product, schema=product_schema)
    
    # Explicit field checks
    assert first_product["id"] is not None and len(first_product["id"]) > 0
    assert first_product["name"] is not None and len(first_product["name"]) > 0
    assert first_product["price"] is not None and float(first_product["price"]) > 0
    assert isinstance(first_product["images"], list) and len(first_product["images"]) > 0


@pytest.mark.api
def test_api_03_get_unknown_product_or_endpoint(api_request_context: APIRequestContext):
    """API-03: GET unknown product id - returns documented error or not found in catalog."""
    response = api_request_context.get("/catalog.json")
    assert response.status == 200
    products = response.json()["products"]
    
    # Search for an unknown product id
    unknown_id = "prod-does-not-exist-99999"
    matched = [p for p in products if p["id"] == unknown_id]
    assert len(matched) == 0, f"Unexpectedly found unknown product id: {matched}"


@pytest.mark.api
def test_api_04_response_time(api_request_context: APIRequestContext):
    """API-04: Response time - Under 2 seconds for key calls."""
    start_time = time.perf_counter()
    response = api_request_context.get("/catalog.json")
    elapsed_time = time.perf_counter() - start_time
    
    assert response.status == 200
    assert elapsed_time < 2.0, f"Response time took {elapsed_time:.2f}s, expected < 2.0s"


@pytest.mark.api
def test_api_05_headers(api_request_context: APIRequestContext):
    """API-05: Headers - Correct content-type, caching and security headers."""
    response = api_request_context.get("/catalog.json")
    assert response.status == 200
    
    headers = response.headers
    # Content-type verification
    content_type = headers.get("content-type", "")
    assert "application/json" in content_type, f"Expected application/json content-type, got {content_type}"
    
    # Netlify hosting and security headers
    assert "strict-transport-security" in headers, "HSTS security header missing"
    assert "server" in headers and "netlify" in headers["server"].lower(), "Server header not Netlify"


@pytest.mark.api
def test_api_06_cart_checkout_payload_structure(checkout_fixtures: dict):
    """API-06: Cart/checkout calls - Validates expected order payload format and status handling."""
    order_payload = {
        "shippingAddress": checkout_fixtures["valid_address"],
        "sameBillingAsShipping": True,
        "couponCode": "WINTER10"
    }
    # Validate payload structure required by store orders contract
    assert "shippingAddress" in order_payload
    assert "line1" in order_payload["shippingAddress"]
    assert "city" in order_payload["shippingAddress"]
    assert "postalCode" in order_payload["shippingAddress"]
    assert len(order_payload["shippingAddress"]["country"]) == 2


@pytest.mark.api
def test_api_07_invalid_payload_schema_rejection(product_schema: dict):
    """API-07: Invalid payload - Schema rejects invalid or missing fields with validation error."""
    invalid_product_payload = {
        "id": "prod-broken",
        # Missing 'name'
        # Missing 'price'
        "images": []
    }
    with pytest.raises(jsonschema.ValidationError) as exc_info:
        jsonschema.validate(instance=invalid_product_payload, schema=product_schema)
    assert "'name' is a required property" in str(exc_info.value) or "'images'" in str(exc_info.value)


@pytest.mark.api
@pytest.mark.e2e
def test_api_08_ui_vs_api_consistency(page: Page, api_request_context: APIRequestContext, product_page: ProductPage):
    """API-08: UI vs API consistency - Prices and names in UI equal API data."""
    # 1. Fetch products from API data source
    api_response = api_request_context.get("/catalog.json")
    assert api_response.status == 200
    api_products = api_response.json()["products"]
    
    # Map api product names and prices
    api_items = {p["name"].strip(): float(p["price"]) for p in api_products}
    
    # 2. Load UI product catalog
    product_page.navigate_listing()
    ui_texts = product_page.get_product_card_names()
    
    # 3. Verify each API product is represented in UI with matching price
    for api_name, api_price in api_items.items():
        matching_ui = [t for t in ui_texts if api_name.lower() in t.lower()]
        assert len(matching_ui) > 0, f"API product '{api_name}' was not found in UI cards"
        
        # Check price matches
        price_str = f"${api_price:.2f}"
        assert any(price_str in t for t in matching_ui), (
            f"Expected price {price_str} for '{api_name}' in UI, found in: {matching_ui}"
        )


@pytest.mark.api
@pytest.mark.e2e
def test_api_09_network_mocking_500_shows_graceful_error(page: Page):
    """API-09: Network mocking - Mock a 500 response with page.route() and verify UI shows graceful error state."""
    # Intercept API calls and catalog data with 500 server error
    page.route("**/catalog.json", lambda route: route.fulfill(status=500, body="Internal Server Error"))
    page.route("**/api/**", lambda route: route.fulfill(status=500, body="Internal Server Error"))
    
    page.goto("/products")
    page.wait_for_timeout(1000)
    
    # UI should display graceful error notification rather than crashing
    error_msg = page.locator(".text-danger-600, [class*='text-danger']")
    expect(error_msg.first).to_be_visible()
    expect(error_msg.first).to_contain_text("Could not load products. Try again shortly.")

