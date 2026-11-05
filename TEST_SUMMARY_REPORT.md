# Northline Store Automation Test Summary Report

**Date**: November 5, 2026  
**Target Application**: [Northline Store (Netlify SPA)](https://ecomcicid.netlify.app/)  
**Framework**: Python 3.11+, Playwright, pytest, pytest-xdist, pytest-html  
**Execution Mode**: Local parallel (4 workers) & Cross-browser execution  

---

## 1. Executive Summary

An end-to-end (E2E) UI and API automation suite was built for the Northline Store e-commerce application. The suite covers shopper journeys from discovery to order placement, free-shipping calculations, form validations, responsive mobile layouts, and API contract/mocking validations.

- **Total Test Cases**: 29
- **Passed**: 29
- **Failed**: 0
- **Pass Rate**: **100%**
- **Full Parallel Execution Time**: ~25 seconds

---

## 2. Test Execution Breakdown

### E2E Test Suite (20 Tests)

| ID | Area | Scenario | Expected Result | Status |
|---|---|---|---|---|
| **E2E-01** | Home | Page loads | Title contains "Northline", header, navigation & footer visible | **PASSED** |
| **E2E-02** | Navigation | Click main menu items | Products, Home, Sign-in navigation with 0 console errors | **PASSED** |
| **E2E-03** | Listing | Open product listing | Shows product cards with image, name, and price | **PASSED** |
| **E2E-04** | Search | Search for known product | Query `?search=chair` displays only matching products | **PASSED** |
| **E2E-05** | Search | Search for nonsense term | Displays "No products match these filters." message | **PASSED** |
| **E2E-06** | Filter/Sort | Sort price low to high | Prices sorted in strict ascending order ($86 to $890) | **PASSED** |
| **E2E-07** | Detail | Open product detail | Displays name, price, description, and active Add to Cart | **PASSED** |
| **E2E-08** | Cart | Add item to cart | Cart count badge updates to `(1)`, item appears in cart | **PASSED** |
| **E2E-09** | Cart | Change quantity | Increasing/decreasing quantity updates subtotal | **PASSED** |
| **E2E-10** | Cart | Remove item | Removing item decreases item count and cart row count | **PASSED** |
| **E2E-11** | Cart | Empty cart | Removing all items displays "Your cart is empty." | **PASSED** |
| **E2E-12** | Shipping | Subtotal below $75 | Shipping charge of $9.99 is applied to subtotal | **PASSED** |
| **E2E-13** | Shipping | Subtotal above $75 | Free shipping applies ($0.00 / "Free") | **PASSED** |
| **E2E-14** | Checkout | Submit empty fields | Field-level required validation errors shown | **PASSED** |
| **E2E-15** | Checkout | Invalid postcode/country | Enforces 2-letter country code and valid postal format | **PASSED** |
| **E2E-16** | Checkout | Valid details | Submits address, reviews order, and completes order | **PASSED** |
| **E2E-17** | Persistence | Reload cart page | Cart state restored from persistent client storage | **PASSED** |
| **E2E-18** | Responsive | Mobile viewport (390x844)| Header, navigation, product view, and cart work on mobile | **PASSED** |
| **E2E-19** | Cross-Browser| Smoke check across engines| Verified across Chromium, Firefox, and WebKit | **PASSED** |
| **E2E-20** | Negative | Invalid URL navigation | Friendly unavailable state with "Back to catalog" link | **PASSED** |

### API Test Suite (9 Tests)

| ID | Check | Endpoint / Contract | Expected Result | Status |
|---|---|---|---|---|
| **API-01** | GET product list | `/catalog.json` | Status 200, non-empty list conforming to JSON schema | **PASSED** |
| **API-02** | GET single product | Product item schema | Validates `id`, `name`, `price`, `images` types and presence | **PASSED** |
| **API-03** | Unknown product | Unknown ID check | Unknown product id not found in catalog | **PASSED** |
| **API-04** | Response time | Key endpoints | Response received in < 2.0s (measured < 0.25s) | **PASSED** |
| **API-05** | Headers | `/catalog.json` | Validates `content-type: application/json` & HSTS headers | **PASSED** |
| **API-06** | Cart/Checkout contract| Order payload structure | Conforms to shippingAddress, country code schema | **PASSED** |
| **API-07** | Invalid payload | Schema validation | Rejects malformed payload with clear validation error | **PASSED** |
| **API-08** | UI vs API consistency | Catalog vs UI Grid | Prices and names rendered on UI match catalog data | **PASSED** |
| **API-09** | Network mocking | Simulated 500 error | Intercepting data calls displays graceful error state | **PASSED** |

---

## 3. Cross-Browser Matrix Results

Smoke tests were executed against all three major browser engines:

| Browser Engine | Tests Executed | Passed | Failed | Duration |
|---|---|---|---|---|
| **Chromium** (Chrome / Edge) | 9 | 9 | 0 | 28.61s |
| **Firefox** (Gecko) | 9 | 9 | 0 | 34.16s |
| **WebKit** (Safari) | 9 | 9 | 0 | 39.07s |

---

## 4. Task 1 Discovery: Page & Endpoint Inventory

During discovery in Task 1, static analysis of the client bundle revealed that the Northline Store is a React Single Page Application (Vite bundle) hosted statically on Netlify Edge:

### Routes Inventory
- `/` — Storefront Home (Hero, Featured Pieces, Categories, Social Proof, Newsletter)
- `/products` — Product Catalog Listing (Category filters, Price range slider, Rating filter, Sorting)
- `/products/:slug` — Product Details (Image gallery, reviews, quantity selector, Add to Cart, Buy Now)
- `/cart` — Shopping Cart & Order Summary (Quantity modifiers, item deletion, promo code input)
- `/checkout` — Multi-step checkout (Step 1: Shipping Address form, Step 2: Review and Place Order)
- `/orders/:id/confirmed` — Post-purchase Order Confirmation screen
- `/login`, `/register`, `/forgot-password`, `/reset-password` — User authentication flows
- `/account`, `/account/orders`, `/account/addresses`, `/account/wishlist` — Shopper account portal

### Data Endpoints & Storage
- Data Source: `/catalog.json` (Static JSON repository containing categories and 6 baseline products).
- Local State Persistence:
  - `ecom-cart` in `window.localStorage` (maintains cart items, quantities, and coupon tokens).
  - `ecom-local-orders` in `window.localStorage` (stores placed orders offline when backend is not connected).
- API Client: Axios instance with base URL `/api`. In this deployment, API requests fall back gracefully to local client storage.

---

## 5. Defects & Observations Found

1. **Defect in `removeItem` (Cart Client Store)**:
   - **Severity**: Low / Minor
   - **Description**: When a shopper removes an individual line item from `/cart`, the application correctly filters the `items` array and decrements `itemCount`. However, the client Zustand store implementation does not recompute `p.subtotal`, causing the previous subtotal to remain visible in the Order Summary until another action (such as quantity update or full page reload) triggers a recalculation.
   - **Recommendation**: In `removeItem(id)`, recalculate `subtotal` like `addItem` does:
     ```javascript
     p.subtotal = p.items.reduce((acc, item) => acc + Number(item.lineTotal), 0).toFixed(2);
     ```

2. **Netlify SPA 200 Fallback for Unknown API Endpoints**:
   - **Severity**: Informational
   - **Description**: Direct `GET` requests to non-existent `/api/*` endpoints return HTTP status `200` with `text/html` content because Netlify's SPA rewrite rules route all unknown requests to `index.html`.
   - **Mitigation in Test Suite**: API contract tests focus on `/catalog.json` and client data structures, validating content types and schemas explicitly.

---

## 6. Acceptance Criteria Verification

- [x] All smoke tests pass on Chromium, Firefox, and WebKit.
- [x] Full suite passes in CI/parallel execution with 0 flaky failures across consecutive runs.
- [x] Every pull request automatically triggers the test suite across browsers.
- [x] Failed tests capture screenshots and Playwright traces for post-mortem debugging.
- [x] Zero hardcoded `time.sleep` calls; all assertions rely on auto-waiting and role/label locators.
