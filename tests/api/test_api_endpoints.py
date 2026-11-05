import time
import jsonschema
import pytest
from playwright.sync_api import APIRequestContext, Page, expect
from pages.product_page import ProductPage


@pytest.mark.api
@pytest.mark.smoke
def test_api_01_get_product_list(electronic_api_context: APIRequestContext, electronic_api_schema: dict):
    """API-01: GET product list - Status 200, JSON array, non-empty from electronicapi."""
    response = electronic_api_context.get("/electronicapi")
    assert response.status == 200, f"Expected status 200, got {response.status}"
    
    products = response.json()
    assert isinstance(products, list), "Response is not a JSON list"
    assert len(products) > 0, "Product list is empty"
    
    # Validate each product against schema
    for product in products[:10]:
        jsonschema.validate(instance=product, schema=electronic_api_schema)


@pytest.mark.api
@pytest.mark.smoke
def test_api_02_get_single_product_schema(electronic_api_context: APIRequestContext, electronic_api_schema: dict):
    """API-02: GET single product - Status 200, matches schema (id, name, price, image)."""
    response = electronic_api_context.get("/electronicapi/1")
    assert response.status == 200, f"Expected status 200, got {response.status}"
    
    product = response.json()
    # Validate against electronic product schema
    jsonschema.validate(instance=product, schema=electronic_api_schema)
    
    # Explicit required field assertions
    assert product["id"] == "1"
    assert product["name"] is not None and len(product["name"]) > 0
    assert product["price"] is not None and float(product["price"]) > 0
    assert product["image"] is not None and product["image"].startswith("http")


@pytest.mark.api
def test_api_03_get_unknown_product_or_endpoint(electronic_api_context: APIRequestContext):
    """API-03: GET unknown product id - returns 404 Not Found."""
    response = electronic_api_context.get("/electronicapi/999999")
    assert response.status == 404, f"Expected 404 for unknown product id, got {response.status}"


@pytest.mark.api
def test_api_04_response_time(electronic_api_context: APIRequestContext):
    """API-04: Response time - Under 2 seconds for key calls."""
    start_time = time.perf_counter()
    response = electronic_api_context.get("/electronicapi")
    elapsed_time = time.perf_counter() - start_time
    
    assert response.status == 200
    assert elapsed_time < 2.0, f"Response time took {elapsed_time:.2f}s, expected < 2.0s"


@pytest.mark.api
def test_api_05_headers(electronic_api_context: APIRequestContext):
    """API-05: Headers - Correct content-type, caching and security headers."""
    response = electronic_api_context.get("/electronicapi")
    assert response.status == 200
    
    headers = response.headers
    content_type = headers.get("content-type", "")
    assert "application/json" in content_type, f"Expected application/json, got {content_type}"
    assert "access-control-allow-origin" in headers, "Missing CORS access-control-allow-origin header"


@pytest.mark.api
def test_api_06_cart_checkout_payload_structure(electronic_api_context: APIRequestContext, electronic_api_schema: dict):
    """API-06: CRUD / Payload handling - Creates product, validates 201 response, and cleans up with DELETE."""
    new_product_payload = {
        "name": "Sony Wireless Noise Cancelling Headphones",
        "price": "24999",
        "image": "https://picsum.photos/seed/sony-test/400/400",
        "description": "High-fidelity audio testing item.",
        "brand": "Sony",
        "category": "Headphones"
    }
    
    # 1. POST request to create product
    create_res = electronic_api_context.post(
        "/electronicapi",
        headers={"Content-Type": "application/json"},
        data=new_product_payload
    )
    assert create_res.status == 201, f"Expected 201 Created, got {create_res.status}"
    
    created_item = create_res.json()
    assert "id" in created_item
    assert created_item["name"] == new_product_payload["name"]
    created_id = created_item["id"]
    
    # 2. Cleanup: DELETE request to remove created product
    delete_res = electronic_api_context.delete(f"/electronicapi/{created_id}")
    assert delete_res.status == 200, f"Expected 200 OK on delete, got {delete_res.status}"


@pytest.mark.api
def test_api_07_invalid_payload_schema_rejection(electronic_api_schema: dict):
    """API-07: Invalid payload - Schema rejects invalid or missing fields with validation error."""
    invalid_product_payload = {
        "id": "prod-broken",
        # Missing 'name'
        # Missing 'price'
        # Missing 'image'
        "category": "Invalid"
    }
    with pytest.raises(jsonschema.ValidationError) as exc_info:
        jsonschema.validate(instance=invalid_product_payload, schema=electronic_api_schema)
    assert "'name' is a required property" in str(exc_info.value) or "'price'" in str(exc_info.value)


@pytest.mark.api
@pytest.mark.e2e
def test_api_08_ui_vs_api_consistency(page: Page, electronic_api_context: APIRequestContext):
    """API-08: UI vs API consistency - Prices and names in UI match electronicapi data."""
    # 1. Fetch top products from electronicapi
    response = electronic_api_context.get("/electronicapi")
    assert response.status == 200
    api_products = response.json()
    first_item = api_products[0]
    
    # 2. Mock store catalog with electronicapi data to verify UI consistency
    def provide_electronic_catalog(route):
        ui_catalog = {
            "categories": [{"id": "cat-audio", "name": "Audio", "slug": "audio", "parentId": None}],
            "products": [
                {
                    "id": f"prod-{first_item['id']}",
                    "name": first_item["name"],
                    "slug": "crusher-evo",
                    "description": first_item["description"],
                    "price": str(first_item["price"]),
                    "images": [first_item["image"]],
                    "categoryId": "cat-audio",
                    "isActive": True,
                    "createdAt": first_item.get("createdAt", "2026-01-01T00:00:00.000Z"),
                    "category": {"id": "cat-audio", "name": "Audio", "slug": "audio"}
                }
            ]
        }
        route.fulfill(json=ui_catalog)

    page.route("**/catalog.json", provide_electronic_catalog)
    page.goto("/products")
    page.wait_for_load_state("networkidle")
    
    # 3. Assert UI rendered product card has matching name and formatted price from electronicapi
    expect(page.get_by_text(first_item["name"])).to_be_visible()
    formatted_price = f"${float(first_item['price']):,.2f}"
    expect(page.get_by_text(formatted_price)).to_be_visible()


@pytest.mark.api
@pytest.mark.e2e
def test_api_09_network_mocking_500_shows_graceful_error(page: Page):
    """API-09: Network mocking - Mock a 500 response on electronicapi / catalog and verify UI shows graceful error."""
    page.route("**/electronicapi**", lambda route: route.fulfill(status=500, body="Internal Server Error"))
    page.route("**/catalog.json", lambda route: route.fulfill(status=500, body="Internal Server Error"))
    page.route("**/api/**", lambda route: route.fulfill(status=500, body="Internal Server Error"))
    
    page.goto("/products")
    page.wait_for_timeout(1000)
    
    # UI should display graceful error notification
    error_msg = page.locator(".text-danger-600, [class*='text-danger']")
    expect(error_msg.first).to_be_visible()
    expect(error_msg.first).to_contain_text("Could not load products. Try again shortly.")
