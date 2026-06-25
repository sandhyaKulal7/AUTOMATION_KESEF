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
# ── TC-34 ──────────────────────────────────────────────────────────────────
    
    @allure.title("TC-34 | First Name Required")
    def test_first_name_required(self, admin_page):
        add = AddDealPage(admin_page)
        add.goto()

        first_name = admin_page.locator(AddDealPage.FIRST_NAME)

        first_name.click()
        admin_page.locator(AddDealPage.LAST_NAME).click()

        errors = add.get_validation_errors()

        print("Validation Errors:", errors)

        assert len(errors) > 0, (
            f"Expected validation error for First Name. Found: {errors}"
        )


    # ── TC-35 ──────────────────────────────────────────────────────────────
    @allure.title("TC-35 | Last Name Required")
    def test_last_name_required(self, admin_page):
        add = AddDealPage(admin_page)
        add.goto()

        last_name = admin_page.locator(AddDealPage.LAST_NAME)

        last_name.click()
        admin_page.locator(AddDealPage.FIRST_NAME).click()

        errors = add.get_validation_errors()

        print("Validation Errors:", errors)

        assert len(errors) > 0, (
            f"Expected validation error for Last Name. Found: {errors}"
        )


    # ── TC-36 ──────────────────────────────────────────────────────────────
    @allure.title("TC-36 | Email Required")
    def test_email_required(self, admin_page):
        add = AddDealPage(admin_page)
        add.goto()

        email = admin_page.locator(AddDealPage.EMAIL)

        email.click()
        admin_page.locator(AddDealPage.FIRST_NAME).click()

        errors = add.get_validation_errors()

        print("Validation Errors:", errors)

        assert len(errors) > 0, (
            f"Expected validation error for Email. Found: {errors}"
        )


    # ── TC-37 ──────────────────────────────────────────────────────────────
    @allure.title("TC-37 | Invalid Email Format")
    def test_invalid_email_format(self, admin_page):
        add = AddDealPage(admin_page)
        add.goto()

        email = admin_page.locator(AddDealPage.EMAIL)

        email.fill("invalidemail")
        email.press("Tab")

        admin_page.wait_for_timeout(1000)

        errors = add.get_validation_errors()

        print("Validation Errors:", errors)

        assert len(errors) > 0, (
            f"Expected invalid email validation. Found: {errors}"
        )


    # ── TC-38 ──────────────────────────────────────────────────────────────
    @allure.title("TC-38 | Phone Number Required")
    def test_phone_number_required(self, admin_page):
        add = AddDealPage(admin_page)
        add.goto()

        phone = admin_page.locator(AddDealPage.PHONE)

        phone.click()
        admin_page.locator(AddDealPage.FIRST_NAME).click()

        errors = add.get_validation_errors()

        print("Validation Errors:", errors)

        assert len(errors) > 0, (
            f"Expected phone number validation error. Found: {errors}"
        )
    # ── TC-34 ──────────────────────────────────────────────────────────────────
        @allure.title("TC-35 | Phone Number is required")
        def test_phone_number_required(self, admin_page):
            add = AddDealPage(admin_page)
            add.goto()

            phone = admin_page.locator(AddDealPage.PHONE)
            phone.fill("9880424798")
            phone.press("Control+a")
            phone.press("Backspace")
            phone.press("Tab")

            errors = add.get_validation_errors()

            assert any(
                "phone number is required" in err.lower()
                for err in errors
            ), f"Expected Phone Number required error. Found: {errors}"
    # ── TC-34 ──────────────────────────────────────────────────────────────────
    @allure.title("TC-34 | Invalid Email Format validation")
    def test_invalid_email_format_message(self, admin_page):
        add = AddDealPage(admin_page)
        add.goto()

        add.fill(AddDealPage.EMAIL, "invalidemail")
        admin_page.locator(AddDealPage.EMAIL).press("Tab")

        errors = add.get_validation_errors()

        assert any(
            "invalid email format" in err.lower()
            for err in errors
        ), f"Expected 'Invalid Email Format' error. Found: {errors}"

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

    @allure.title("TC-39 | Business City Required")
    def test_business_city_required(self, admin_page):
        add = AddDealPage(admin_page)
        add.goto()

        city = admin_page.locator(AddDealPage.BUSINESS_CITY)

        city.click()
        admin_page.locator(AddDealPage.FIRST_NAME).click()

        errors = add.get_validation_errors()

        print("Validation Errors:", errors)

        assert len(errors) > 0

    @allure.title("TC-40 | Business City Numbers Only")
    def test_business_city_numbers_only(self, admin_page):
        add = AddDealPage(admin_page)
        add.goto()

        city = admin_page.locator(AddDealPage.BUSINESS_CITY)

        city.fill("123456")
        city.press("Tab")

        admin_page.wait_for_timeout(1000)

        errors = add.get_validation_errors()

        print("Validation Errors:", errors)

        assert len(errors) > 0

    @allure.title("TC-42 | Business Street Numbers Only")
    def test_business_street_numbers_only(self, admin_page):
        add = AddDealPage(admin_page)
        add.goto()

        street = admin_page.locator(AddDealPage.BUSINESS_STREET)

        street.fill("123456789")
        street.press("Tab")

        admin_page.wait_for_timeout(1000)

        errors = add.get_validation_errors()

        print("Validation Errors:", errors)

        assert len(errors) > 0

    @allure.title("TC-43 | Business Postal Code Required")
    def test_business_postal_code_required(self, admin_page):
        add = AddDealPage(admin_page)
        add.goto()

        postal = admin_page.locator(AddDealPage.BUSINESS_POSTAL_CODE)

        postal.click()
        admin_page.locator(AddDealPage.FIRST_NAME).click()

        errors = add.get_validation_errors()

        print("Validation Errors:", errors)

        assert len(errors) > 0
    @allure.title("TC-44 | Funding Amount Required")
    def test_funding_amount_required(self, admin_page):
        add = AddDealPage(admin_page)
        add.goto()

        add.fill_client_details_auto()
        add.click_next_step1()
        add.fill_lead_details_auto()
        add.click_next_step2()

        funding = admin_page.locator(AddDealPage.FUNDING_AMOUNT)

        funding.click()
        admin_page.locator(AddDealPage.FACTOR_RATE).click()

        errors = add.get_validation_errors()

        print("Validation Errors:", errors)

        assert len(errors) > 0

    # ── TC-45 ──────────────────────────────────────────────────────────────
    @allure.title("TC-45 | Funding Amount Negative")
    def test_funding_amount_negative(self, admin_page):
        add = AddDealPage(admin_page)
        add.goto()

        add.fill_client_details_auto()
        add.click_next_step1()
        add.fill_lead_details_auto()
        add.click_next_step2()

        funding = admin_page.locator(AddDealPage.FUNDING_AMOUNT)

        funding.click()
        funding.press("Control+A")
        funding.fill("-1000")
        funding.press("Tab")

        admin_page.wait_for_timeout(1500)

        errors = add.get_validation_errors()
        submit_enabled = admin_page.get_by_role(
            "button",
            name="Submit"
        ).is_enabled()

        print("Validation Errors:", errors)
        print("Submit Enabled:", submit_enabled)

        assert errors or not submit_enabled, (
            "Negative Funding Amount should show validation "
            "or disable Submit button"
        )


    # ── TC-46 ──────────────────────────────────────────────────────────────
    @allure.title("TC-46 | Funding Amount Zero")
    def test_funding_amount_zero(self, admin_page):
        add = AddDealPage(admin_page)
        add.goto()

        add.fill_client_details_auto()
        add.click_next_step1()
        add.fill_lead_details_auto()
        add.click_next_step2()

        funding = admin_page.locator(AddDealPage.FUNDING_AMOUNT)

        funding.click()
        funding.press("Control+A")
        funding.fill("0")
        funding.press("Tab")

        admin_page.wait_for_timeout(1500)

        errors = add.get_validation_errors()
        submit_enabled = admin_page.get_by_role(
            "button",
            name="Submit"
        ).is_enabled()

        print("Validation Errors:", errors)
        print("Submit Enabled:", submit_enabled)

        assert errors or not submit_enabled, (
            "Funding Amount = 0 should show validation "
            "or disable Submit button"
        )


    # ── TC-47 ──────────────────────────────────────────────────────────────
    @allure.title("TC-47 | Factor Rate Required")
    def test_factor_rate_required(self, admin_page):
        add = AddDealPage(admin_page)
        add.goto()

        add.fill_client_details_auto()
        add.click_next_step1()
        add.fill_lead_details_auto()
        add.click_next_step2()

        factor = admin_page.locator(AddDealPage.FACTOR_RATE)

        factor.click()
        factor.press("Control+A")
        factor.press("Backspace")
        factor.press("Tab")

        admin_page.wait_for_timeout(1500)

        errors = add.get_validation_errors()
        submit_enabled = admin_page.get_by_role(
            "button",
            name="Submit"
        ).is_enabled()

        print("Validation Errors:", errors)
        print("Submit Enabled:", submit_enabled)

        assert errors or not submit_enabled, (
            "Empty Factor Rate should show validation "
            "or disable Submit button"
        )


    # ── TC-48 ──────────────────────────────────────────────────────────────
    @allure.title("TC-48 | Factor Rate Negative")
    def test_factor_rate_negative(self, admin_page):
        add = AddDealPage(admin_page)
        add.goto()

        add.fill_client_details_auto()
        add.click_next_step1()
        add.fill_lead_details_auto()
        add.click_next_step2()

        factor = admin_page.locator(AddDealPage.FACTOR_RATE)

        factor.click()
        factor.press("Control+A")
        factor.fill("-5")
        factor.press("Tab")

        admin_page.wait_for_timeout(1500)

        errors = add.get_validation_errors()
        submit_enabled = admin_page.get_by_role(
            "button",
            name="Submit"
        ).is_enabled()

        print("Validation Errors:", errors)
        print("Submit Enabled:", submit_enabled)

        assert errors or not submit_enabled, (
            "Negative Factor Rate should show validation "
            "or disable Submit button"
        )
    @allure.title("TC-52 | Payment Amount Zero")
    def test_payment_amount_zero(self, admin_page):
        add = AddDealPage(admin_page)
        add.goto()

        add.fill_client_details_auto()
        add.click_next_step1()
        add.fill_lead_details_auto()
        add.click_next_step2()

        payment = admin_page.get_by_role(
            "textbox",
            name="Payment Amount"
        )

        payment.fill("0")
        payment.press("Tab")

        expect(
            admin_page.get_by_text(
                "Payment Amount must not be 0"
            )
        ).to_be_visible()

    @allure.title("TC-56 | Weekly Frequency Selection")
    def test_weekly_frequency_selection(self, admin_page):
        add = AddDealPage(admin_page)
        add.goto()

        add.fill_client_details_auto()
        add.click_next_step1()
        add.fill_lead_details_auto()
        add.click_next_step2()

        weekly = admin_page.get_by_role(
            "radio",
            name="Weekly"
        )

        weekly.check()

        expect(weekly).to_be_checked()

    @allure.title("TC-55 | Daily Frequency Selection")
    def test_daily_frequency_selection(self, admin_page):
        add = AddDealPage(admin_page)
        add.goto()

        add.fill_client_details_auto()
        add.click_next_step1()
        add.fill_lead_details_auto()
        add.click_next_step2()

        daily = admin_page.get_by_role(
            "radio",
            name="Daily"
        )

        daily.check()

        expect(daily).to_be_checked()