# Northline Store Automation Test Suite (Python Playwright)

[![Northline Tests](https://github.com/imjay44/PlaywrightAssessment/actions/workflows/tests.yml/badge.svg)](https://github.com/imjay44/PlaywrightAssessment/actions/workflows/tests.yml)

Automated end-to-end (E2E) UI and API testing framework for the [Northline Store](https://ecomcicid.netlify.app/) e-commerce web application, built with **Python 3.11+**, **Playwright**, **pytest**, and **GitHub Actions**.

---

## 📋 Table of Contents
- [Architecture & Tech Stack](#-architecture--tech-stack)
- [Directory Structure](#-directory-structure)
- [Prerequisites & Installation](#-prerequisites--installation)
- [Running Tests](#-running-tests)
- [Page Object Model (POM) Design](#-page-object-model-pom-design)
- [CI/CD Pipeline (GitHub Actions)](#-cicd-pipeline-github-actions)
- [Adding New Tests](#-adding-new-tests)
- [Test Inventory & Results](#-test-inventory--results)

---

## 🛠 Architecture & Tech Stack

| Component | Tool / Library | Purpose |
|---|---|---|
| **Language** | Python 3.11+ | Test framework core language |
| **Automation Engine** | `playwright`, `pytest-playwright` | Multi-browser automation (Chromium, Firefox, WebKit) |
| **Test Runner** | `pytest` | Test execution, fixtures, test discovery, and markers |
| **Parallel Execution**| `pytest-xdist` | Multi-worker parallel test runs |
| **Reporting** | `pytest-html` | Standalone HTML test execution report with failure traces |
| **Schema Validation** | `jsonschema` | JSON schema contract testing for API data sources |
| **Test Data & Fixtures** | JSON Fixtures, `Faker` | Decoupled data contracts and randomized test inputs |
| **CI/CD** | GitHub Actions | Automated build, matrix testing, and artifact publishing |

---

## 📁 Directory Structure

```text
northline-tests/
├── .github/
│   └── workflows/
│       └── tests.yml            # CI/CD multi-browser matrix workflow
├── pages/                       # Page Object Model (POM) classes
│   ├── __init__.py
│   ├── home_page.py             # Home page elements and user actions
│   ├── product_page.py          # Product catalog, filter/sort & detail pages
│   ├── cart_page.py             # Shopping cart, line totals, and shipping rules
│   └── checkout_page.py         # Checkout multi-step form & order confirmation
├── tests/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── test_api_endpoints.py # 9 API contract, response time & mocking tests
│   └── e2e/
│       ├── __init__.py
│       ├── test_home_navigation.py       # Home page & navigation tests (E2E-01, 02, 20)
│       ├── test_products.py              # Catalog, search, sort, detail (E2E-03 - 07)
│       ├── test_cart.py                  # Cart actions, quantities & shipping (E2E-08 - 13, 17)
│       ├── test_checkout.py              # Form validation & order placement (E2E-14 - 16)
│       └── test_responsive_crossbrowser.py # Mobile 390x844 & engine smoke (E2E-18, 19)
├── data/
│   ├── catalog_schema.json      # JSON schema for product catalog endpoint
│   ├── product_schema.json      # JSON schema for individual product objects
│   └── checkout_data.json       # Fixtures for checkout address payloads
├── conftest.py                  # Pytest fixtures (contexts, POM instances, schemas)
├── pytest.ini                   # Pytest configuration, flags, and markers
├── requirements.txt             # Framework dependencies
├── TEST_SUMMARY_REPORT.md       # Test execution report and defect analysis
└── README.md
```

---

## ⚙️ Prerequisites & Installation

### 1. Clone & Set Up Virtual Environment

```bash
# Clone the repository
git clone <repo-url>
cd <repo-folder>

# Create and activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies & Playwright Browsers

```bash
pip install -r requirements.txt
playwright install --with-deps chromium firefox webkit
```

---

## 🚀 Running Tests

### Quick Critical Smoke Tests (Fail-Fast)
Runs the critical user journeys (Home, Listing, Detail, Cart, Checkout, Cross-browser):
```bash
pytest -m smoke
```

### Run Full Regression Suite in Parallel (Default: 4 Workers)
```bash
pytest -n 4
```

### Run Only API Tests
```bash
pytest tests/api
```

### Run Only E2E Tests
```bash
pytest tests/e2e
```

### Run Cross-Browser Smoke Tests
```bash
# Run on Chromium
pytest -m smoke --browser chromium

# Run on Firefox
pytest -m smoke --browser firefox

# Run on WebKit (Safari engine)
pytest -m smoke --browser webkit
```

### Run in Headed Mode with Slow-Motion (Local Debugging)
```bash
pytest --headed --slowmo 300 -k "test_e2e_16"
```

### View Traces and Reports
A self-contained HTML report is automatically generated at `reports/report.html`.
To view Playwright traces for any failed tests:
```bash
playwright show-trace test-results/<test_folder>/trace.zip
```

---

## 🏛 Page Object Model (POM) Design

All UI locators are encapsulated inside dedicated page classes under `pages/`:
- **Role & Label Based Locators**: Locators prioritize accessible queries (`get_by_role`, `get_by_label`, `get_by_text`) rather than brittle CSS/XPath selectors.
- **Auto-Waiting**: Tests leverage Playwright's built-in auto-waiting and assertion retries (`expect(locator).to_be_visible()`, `expect(locator).to_have_text(...)`), completely eliminating `time.sleep`.
- **Decoupled Test Logic**: Tests focus purely on business logic assertions; UI hierarchy changes require updates solely in the respective Page Object.

---

## 🔄 CI/CD Pipeline (GitHub Actions)

The pipeline is defined in `.github/workflows/tests.yml`:
1. **Triggers**: Runs automatically on every `push` to `main`, on every `pull_request`, nightly at 02:00 UTC via `schedule`, and on-demand via `workflow_dispatch`.
2. **Cross-Browser Matrix**: Spawns parallel matrix runners across `chromium`, `firefox`, and `webkit`.
3. **Fail-Fast Smoke Stage**: Executes smoke tests first to catch critical breakages early before running the full regression suite.
4. **Artifact Publishing**: Publishes HTML test reports, screenshots, and Playwright traces as downloadable build artifacts (`actions/upload-artifact@v4`).

---

## ➕ Adding New Tests

1. **Add Locators & Methods to Page Object**:
   If adding an action for the cart, add the locator and interaction method to `pages/cart_page.py`.
2. **Create Test Function**:
   Create a test under `tests/e2e/test_<feature>.py`:
   ```python
   import pytest
   from playwright.sync_api import Page, expect
   from pages.cart_page import CartPage

   @pytest.mark.e2e
   def test_new_cart_feature(page: Page, cart_page: CartPage):
       cart_page.navigate()
       # assertions using expect(...)
       expect(cart_page.cart_heading).to_be_visible()
   ```
3. **Tag Markers**: Tag with `@pytest.mark.smoke`, `@pytest.mark.e2e`, or `@pytest.mark.api` as appropriate.
4. **Run Locally**: Verify with `pytest -k "test_new_cart_feature"`.

---

## 📊 Test Inventory & Results

See [TEST_SUMMARY_REPORT.md](TEST_SUMMARY_REPORT.md) for full execution results, pass/fail counts, and defect analysis.

