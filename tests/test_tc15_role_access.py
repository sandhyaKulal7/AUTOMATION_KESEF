"""
test_tc15_role_access.py — Role-based access control

Only an ADMIN credential is currently available in .env. The non-admin checks
are credential-gated: each skips unless a dedicated <ROLE>_EMAIL is set, so they
never fall back to the admin user (which would assert the wrong thing). They
carry real assertions, so they execute meaningfully the moment role credentials
are provided — set INVESTOR_EMAIL / VIEWER_EMAIL / SALES_EMAIL (+ _PASSWORD).
"""
import os
import re
import pytest
import allure
from playwright.sync_api import expect


def _needs(role_env: str) -> bool:
    """True when the role's dedicated credential is NOT configured."""
    return not os.environ.get(role_env)


def _final_url(page, path: str) -> str:
    page.goto(path, wait_until="domcontentloaded")
    page.wait_for_timeout(1500)
    return page.url


def _assert_allowed(page, path: str):
    url = _final_url(page, path)
    assert path in url, f"Role should be allowed on {path}, but landed on {url}"


def _assert_denied(page, path: str):
    url = _final_url(page, path)
    # A denied protected route bounces back to login / root / a redirect URL.
    assert path not in url, f"Role should be denied {path}, but stayed on {url}"


@allure.suite("15 — Role Access Control")
@pytest.mark.role_access
@pytest.mark.regression
class TestRoleAccess:

    @allure.title("TC-157 | Investor cannot access Merchant List (/client-portal)")
    @pytest.mark.skipif(_needs("INVESTOR_EMAIL"), reason="No dedicated INVESTOR credential")
    def test_investor_no_merchant_list(self, investor_page):
        _assert_denied(investor_page, "/client-portal")

    @allure.title("TC-158 | Investor can access Reports page")
    @pytest.mark.skipif(_needs("INVESTOR_EMAIL"), reason="No dedicated INVESTOR credential")
    def test_investor_can_access_reports(self, investor_page):
        _assert_allowed(investor_page, "/reports")

    @allure.title("TC-159 | Viewer cannot access Add Deal page")
    @pytest.mark.skipif(_needs("VIEWER_EMAIL"), reason="No dedicated VIEWER credential")
    def test_viewer_no_add_deal(self, viewer_page):
        _assert_denied(viewer_page, "/add-client")

    @allure.title("TC-160 | Viewer cannot access Control Panel")
    @pytest.mark.skipif(_needs("VIEWER_EMAIL"), reason="No dedicated VIEWER credential")
    def test_viewer_no_control_panel(self, viewer_page):
        _assert_denied(viewer_page, "/control-panel")

    @allure.title("TC-162 | Sales role cannot access Control Panel")
    @pytest.mark.skipif(_needs("SALES_EMAIL"), reason="No dedicated SALES credential")
    def test_sales_no_control_panel(self, sales_page):
        _assert_denied(sales_page, "/control-panel")

    @allure.title("TC-165 | Admin can access all pages without restriction")
    def test_admin_full_access(self, admin_page):
        # Don't wait for networkidle — dashboards poll in the background and never
        # go idle. domcontentloaded + a URL assertion proves the route was allowed
        # (an unauthorized route would bounce back to "/?redirect=...").
        for path in ["/dashboard", "/client-portal", "/add-client", "/reports", "/control-panel"]:
            admin_page.goto(path, wait_until="domcontentloaded")
            expect(admin_page).to_have_url(re.compile(re.escape(path)))
