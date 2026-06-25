"""
test_tc03_add_deal.py — TC-24 through TC-33: Add Deal form

All tests use "Fill Test Data" to fast-track through earlier steps so that
validation tests on Step 3 fields (TC-26, TC-27) are fully reachable.
TC-30 uses Fill Test Data on all three steps and creates a real deal.
"""
import pytest
import allure
from playwright.sync_api import expect
from pages.add_deal_page import AddDealPage


@allure.suite("03 — Add Deal")
@pytest.mark.ui
@pytest.mark.regression
class TestAddDeal:

    # ── TC-24 ──────────────────────────────────────────────────────────────────
    @allure.title("TC-24 | Empty form submission shows validation errors")
    def test_empty_form_shows_errors(self, admin_page):
        """Clicking Next on a blank form fires a toast/snackbar or inline errors."""
        add = AddDealPage(admin_page)
        add.goto()
        add.click_next()
        add.assert_has_validation_errors()

    # ── TC-25 ──────────────────────────────────────────────────────────────────
    @allure.title("TC-25 | Invalid email format is rejected")
    def test_invalid_email_rejected(self, admin_page):
        """Typing a non-email string and clicking Next must show an error."""
        add = AddDealPage(admin_page)
        add.goto()
        add.fill(AddDealPage.EMAIL, "notavalidemail")
        add.click_next()
        add.assert_has_validation_errors()

    # ── TC-26 ──────────────────────────────────────────────────────────────────
   
    # ── TC-27 ──────────────────────────────────────────────────────────────────
    @allure.title("TC-27 | Negative funding amount is rejected")
    def test_negative_funding_amount(self, admin_page):
        """
        Auto-fill Steps 1 and 2 via Fill Test Data to reach Funding Details,
        then enter a negative Funding Amount.
        Expects an inline error or a disabled Submit button.
        """
        add = AddDealPage(admin_page)
        add.goto()

        add.fill_client_details_auto()
        add.click_next_step1()
        add.fill_lead_details_auto()
        add.click_next_step2()

        amount_field = admin_page.locator(AddDealPage.FUNDING_AMOUNT)
        amount_field.click()
        amount_field.press("Control+a")
        amount_field.fill("-1000")
        amount_field.press("Tab")
        admin_page.wait_for_timeout(800)

        errors = add.get_validation_errors()
        all_text = " ".join(e.lower() for e in errors)
        try:
            snackbar = admin_page.locator(AddDealPage.SNACKBAR_ALERT).first
            snackbar.wait_for(state="visible", timeout=2000)
            all_text += " " + snackbar.inner_text().lower()
        except Exception:
            pass

        submit_enabled = admin_page.get_by_role("button", name="Submit").is_enabled()
        has_error = any(kw in all_text for kw in ("amount", "negative", "positive", "invalid", "must"))
        assert has_error or not submit_enabled, (
            f"Expected a funding amount error or disabled Submit. Errors: {all_text!r}"
        )

    # ── TC-30 ──────────────────────────────────────────────────────────────────
    @allure.title("TC-30 | Auto-fill all 3 steps then Submit and Create deal")
    @pytest.mark.smoke
    def test_create_deal_via_fill_test_data(self, admin_page):
        """
        Fill Test Data on all three steps populates every required field.
        Submit -> Create should produce a success confirmation.
        """
        add = AddDealPage(admin_page)
        add.goto()
 
        add.fill_client_details_auto()
        add.click_next_step1()
        add.fill_lead_details_auto()
        add.click_next_step2()
        add.fill_funding_details_auto()
        add.fill_buyout_details_auto()
        add.fill_deal_documents_auto()

        add.submit()
        add.click_create()
 
        assert add.is_deal_created_confirmation_displayed(), (
            "Deal creation confirmation (success toast or snackbar) should be visible"
        )

    # ── TC-32 ──────────────────────────────────────────────────────────────────
    @allure.title("TC-32 | Save as Draft — saved draft appears in the Drafts tab")
    def test_save_as_draft(self, admin_page):
        """
        Filling only First Name + Last Name enables Save as Draft.
        After saving, the unique name must be visible in the Drafts tab.
        """
        from faker import Faker
        unique_name = f"AutoDraft{Faker().random_number(digits=8)}"

        add = AddDealPage(admin_page)
        add.goto()
        add.fill(AddDealPage.FIRST_NAME, unique_name)
        add.fill(AddDealPage.LAST_NAME, "User")

        draft_btn = admin_page.get_by_role("button", name="Save as Draft").first
        expect(draft_btn).to_be_enabled(timeout=5000)

        add.save_draft()

        add.select_drafts_mode()
        expect(
            admin_page.get_by_text(unique_name, exact=False).first
        ).to_be_visible(timeout=10000)
