"""
conftest.py — central pytest configuration
All fixtures, browser setup, and shared hooks live here.
No test logic — only infrastructure.

Login strategy:
  - App root URL (BASE_URL) shows the login form — do NOT navigate to /login
  - Locators are XPath — the live app has zero data-testid attributes
  - context is class-scoped so each test class logs in once
  - page fixture auto-detects an expired session and re-logs in
"""
import os
import json
import pytest
import allure
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

# ── Config ────────────────────────────────────────────────────────────────────
BASE_URL        = os.environ.get("BASE_URL", "https://kesef.qa.codezyng.com/")
BROWSER_TYPE    = os.getenv("BROWSER", "chromium")
SLOW_MO         = int(os.getenv("SLOW_MO", "80"))
DEFAULT_TIMEOUT = int(os.getenv("TIMEOUT", "10000"))

REPORTS_DIR = Path(__file__).resolve().parent / "reports" / "screenshots"

# XPath locators — matches the live KESEF app
_EMAIL_INPUT  = "//input[@name='email']"
_PASSWORD_INPUT = "//input[@name='password']"
_SIGN_IN_BTN  = "//button[text()='Sign In']"


def _is_headless() -> bool:
    return (
        os.environ.get("HEADLESS", "").lower() == "true"
        or os.environ.get("CI", "").lower() == "true"
        or os.environ.get("GITHUB_ACTIONS", "").lower() == "true"
    )


def _get_credentials(role: str = "default") -> dict:
    """
    Return credentials for the given role.
    Falls back to TEST_EMAIL / TEST_PASSWORD for the default (QA admin) user.
    Role-specific vars: ADMIN_EMAIL / ADMIN_PASSWORD, VIEWER_EMAIL / VIEWER_PASSWORD, etc.
    """
    role_upper = role.upper()
    email    = os.environ.get(f"{role_upper}_EMAIL")    or os.environ.get("TEST_EMAIL")
    password = os.environ.get(f"{role_upper}_PASSWORD") or os.environ.get("TEST_PASSWORD")
    if not (email and password):
        raise RuntimeError(
            f"Credentials missing for role '{role}'. "
            "Set TEST_EMAIL / TEST_PASSWORD (or ADMIN_EMAIL / ADMIN_PASSWORD etc.) "
            "in your .env file."
        )
    return {"email": email, "password": password}


def _login(page: Page, role: str = "default") -> None:
    """Fill login form with XPath locators and wait for the app to load."""
    creds = _get_credentials(role)
    page.locator(_EMAIL_INPUT).wait_for(state="visible", timeout=15000)
    page.locator(_EMAIL_INPUT).fill(creds["email"])
    page.locator(_PASSWORD_INPUT).fill(creds["password"])
    page.locator(_SIGN_IN_BTN).click()
    # Wait for the post-login SPA transition to /client-portal so the auth state
    # is fully established. Without this, a subsequent hard goto() to a protected
    # route runs before the guard is ready and bounces back to the login page.
    page.wait_for_url("**/client-portal", timeout=20000)
    page.wait_for_load_state("networkidle", timeout=20000)


# ── Browser (session-scoped — one browser per test run) ───────────────────────
@pytest.fixture(scope="session")
def browser():
    launch_args = ["--disable-blink-features=AutomationControlled"]
    # In headed mode, maximize the window so the (right-aligned) login card and
    # full app layout are visible instead of spilling off-screen.
    if not _is_headless():
        launch_args.append("--start-maximized")
    with sync_playwright() as p:
        b = getattr(p, BROWSER_TYPE).launch(
            headless=_is_headless(),
            slow_mo=SLOW_MO,
            args=launch_args,
        )
        yield b
        b.close()


def _context_kwargs() -> dict:
    """
    Context options. Headless uses a fixed 1920×1080 viewport for deterministic
    layout; headed uses the real (maximized) window size so nothing is clipped.
    """
    kwargs = {"base_url": BASE_URL}
    if _is_headless():
        kwargs["viewport"] = {"width": 1920, "height": 1080}
    else:
        kwargs["no_viewport"] = True
    return kwargs


# ── Context (class-scoped — one login per test class) ─────────────────────────
@pytest.fixture(scope="class")
def context(browser: Browser):
    # base_url lets tests/page-objects use relative paths like page.goto("/dashboard")
    ctx = browser.new_context(**_context_kwargs())
    ctx.set_default_timeout(DEFAULT_TIMEOUT)
    yield ctx
    ctx.close()


# ── Authenticated page fixture ────────────────────────────────────────────────
@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Page:
    """
    Authenticated page for each test.
    Navigates to BASE_URL; auto-logs in if the session has expired.
    """
    p = context.new_page()
    p.set_default_timeout(DEFAULT_TIMEOUT)
    p.goto(BASE_URL, wait_until="networkidle", timeout=30000)
    p.wait_for_timeout(800)

    # Auto-login if the login form is visible (session not restored)
    if p.locator(_EMAIL_INPUT).is_visible():
        _login(p)

    yield p
    p.close()


# ── Unauthenticated page (for login-UI tests only) ────────────────────────────
@pytest.fixture(scope="function")
def fresh_page(browser: Browser) -> Page:
    """Unauthenticated page — for login screen UI tests only."""
    ctx = browser.new_context(**_context_kwargs())
    ctx.set_default_timeout(DEFAULT_TIMEOUT)
    p = ctx.new_page()
    p.goto(BASE_URL, wait_until="networkidle", timeout=30000)
    yield p
    ctx.close()


# ── Role-specific page fixtures ───────────────────────────────────────────────
def _make_role_page(browser: Browser, role: str) -> Page:
    ctx = browser.new_context(**_context_kwargs())
    ctx.set_default_timeout(DEFAULT_TIMEOUT)
    p = ctx.new_page()
    p.goto(BASE_URL, wait_until="networkidle", timeout=30000)
    p.wait_for_timeout(800)
    if p.locator(_EMAIL_INPUT).is_visible():
        _login(p, role)
    return p, ctx


@pytest.fixture(scope="function")
def admin_page(browser: Browser):
    p, ctx = _make_role_page(browser, "admin")
    yield p
    ctx.close()


@pytest.fixture(scope="function")
def viewer_page(browser: Browser):
    p, ctx = _make_role_page(browser, "viewer")
    yield p
    ctx.close()


@pytest.fixture(scope="function")
def investor_page(browser: Browser):
    p, ctx = _make_role_page(browser, "investor")
    yield p
    ctx.close()


@pytest.fixture(scope="function")
def sales_page(browser: Browser):
    p, ctx = _make_role_page(browser, "sales")
    yield p
    ctx.close()


@pytest.fixture(scope="function")
def collections_page(browser: Browser):
    p, ctx = _make_role_page(browser, "collections")
    yield p
    ctx.close()


# ── Test data fixtures ────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def credentials():
    return _get_credentials()


@pytest.fixture(scope="session")
def deal_data():
    path = Path(__file__).parent / "fixtures" / "deal_data.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


@pytest.fixture(scope="session")
def client_data():
    path = Path(__file__).parent / "fixtures" / "client_data.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


# ── Screenshot on failure ─────────────────────────────────────────────────────
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        page_obj = None
        for fixture_name in ("page", "fresh_page", "admin_page", "viewer_page",
                             "investor_page", "sales_page", "collections_page"):
            if fixture_name in item.funcargs:
                page_obj = item.funcargs[fixture_name]
                break
        if page_obj is not None:
            try:
                REPORTS_DIR.mkdir(parents=True, exist_ok=True)
                dest = REPORTS_DIR / f"{item.name}.png"
                page_obj.screenshot(path=str(dest), full_page=True)
                try:
                    allure.attach.file(
                        str(dest),
                        name=item.name,
                        attachment_type=allure.attachment_type.PNG,
                    )
                except Exception:
                    pass
            except Exception:
                # Page may already be closed — silently skip screenshot
                pass
