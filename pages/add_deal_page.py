"""
add_deal_page.py — Add Deal page object (KESEF QA)

Supports two form-filling strategies:
  AUTO   — click each step's "Fill Test Data" button (fast path for smoke / regression)
  MANUAL — type every field explicitly (for validation, data-driven, and field-level tests)

Form architecture — 3-step accordion:
  Step 1 — Client Details  : always expanded on page load
  Step 2 — Lead Details    : unlocks only after Step 1 passes live API validation
  Step 3 — Funding Details : unlocks only after Step 2 is filled
  Deal Documents           : required section; Submit stays disabled until filled

Validation signals:
  Inline MUI helper text  -> p.MuiFormHelperText-root.Mui-error
  Notistack snackbar      -> [role='alert']
"""
import allure
from playwright.sync_api import Page, expect
from pages.base_page import BasePage

DEFAULT_TIMEOUT = 10_000
LONG_TIMEOUT    = 20_000


class AddDealPage(BasePage):

    # Mode labels
    MODE_NEW_CLIENT      = "New Client"
    MODE_EXISTING_CLIENT = "Existing Client"
    MODE_DRAFTS          = "Drafts"

    # Step 1 — Client Details
    FIRST_NAME           = "input[name='firstName']"
    LAST_NAME            = "input[name='lastName']"
    EMAIL                = "input[name='clientEmail']"
    PHONE                = "input[name='clientPhone']"
    DOB                  = "input[name='dob']"
    SIN                  = "input[name='sin']"
    ID_NUMBER            = "input[name='idNumber']"
    ID_EXPIRY            = "input[name='idExpiryDate']"
    HOME_ADDRESS         = "[name='homeAddress']"
    LEGAL_BUSINESS_NAME  = "input[name='legalBusinessName']"
    CORPORATION_NUMBER   = "input[name='corporationNumber']"
    DOING_BUSINESS_AS    = "input[name='doingBusinessAs']"
    BUSINESS_CITY        = "input[name='businessCity']"
    BUSINESS_STREET      = "input[name='businessAddress']"
    BUSINESS_POSTAL_CODE = "input[name='businessPostalCode']"
    AVG_MONTHLY_REVENUE  = "input[name='averageMonthlyRevenue']"
    OWNERSHIP_PCT        = "input[name='primaryOwnershipPercentage']"

    # Step 1 — MUI Select dropdowns
    OWN_HOME_SELECT      = "#mui-component-select-ownHome"
    ID_TYPE_SELECT       = "#mui-component-select-idType"
    CREDIT_SCORE_SELECT  = "#mui-component-select-creditScore"
    CORP_TYPE_SELECT     = "#mui-component-select-corporationType"
    INDUSTRY_SELECT      = "#mui-component-select-industryId"
    BIZ_PROVINCE_SELECT  = "#mui-component-select-businessProvinceId"

    # Step 1 — label constants
    INDUSTRY_LABEL       = "Industry"
    OWN_HOME_LABEL       = "Is the Home Rented or Owned?"
    ID_TYPE_LABEL        = "Identification Type"
    CREDIT_SCORE_LABEL   = "Credit Score"
    CORP_TYPE_LABEL      = "Corporation Type"
    BIZ_PROVINCE_LABEL   = "Business Province"

    # Step 2 — Lead Details
    BROKERAGE_SELECT     = "#mui-component-select-brokerageId"
    UNDERWRITER_SELECT   = "#mui-component-select-underwriterId"
    MERCHANT_CALL_SELECT = "#mui-component-select-merchantCallBy"
    BROKER_COMMISSION    = "input[name='brokerCommissionPercentage']"
    BROKERAGE_LABEL      = "Select the Brokerage"
    UNDERWRITER_LABEL    = "Underwriter"
    MERCHANT_CALL_LABEL  = "Merchant Call By"

    # Step 3 — Funding Details
    INSTITUTION_NUMBER   = "input[name='institutionNumber']"
    TRANSIT_NUMBER       = "input[name='transitNumber']"
    ACCOUNT_NUMBER       = "input[name='accountNumber']"
    SEC_INSTITUTION_NO   = "input[name='secondaryInstitutionNumber']"
    SEC_TRANSIT_NUMBER   = "input[name='secondaryTransitNumber']"
    SEC_ACCOUNT_NUMBER   = "input[name='secondaryAccountNumber']"
    FUNDING_AMOUNT       = "input[name='fundingAmount']"
    FACTOR_RATE          = "input[name='factorRate']"
    UW_FEE_PCT           = "input[name='underwritingFeePercentage']"
    UW_FEE               = "input[name='underwritingFee']"
    PAD_FEE              = "input[name='padFee']"
    NUM_PAYMENTS         = "input[name='numberOfPayments']"
    PAYMENT_FREQ_DAILY   = "input[name='paymentFrequency'][value='DAILY']"
    PAYMENT_FREQ_WEEKLY  = "input[name='paymentFrequency'][value='WEEKLY']"
    AVG_MONTHLY_SALES    = "input[name='averageMonthlySales']"
    NOTES                = "[name='notes']"
    COST_OF_BORROWING    = "input[name='costOfBorrowing']"
    TOTAL_PAYABLE        = "input[name='totalPayable']"
    AMOUNT_CREDITED      = "input[name='amountCredited']"
    PAYMENT_AMOUNT       = "input[name='paymentAmount']"
    BROKERAGE_COMMISSION = "input[name='brokerageCommission']"
    # ── Step 3 — Buyout block (rendered only when "Is this a Buyout Deal?" = Yes) ─
    BUYOUT_YES_RADIO     = ("//*[contains(normalize-space(.),'Is this a Buyout Deal')]"
                            "/following::input[@value='true'][1]")
    BUYOUT_SOURCE_BOX    = ("//input[@name='buyoutDetails.0.lenderId']"
                            "/ancestor::div[contains(@class,'MuiInputBase-root')][1]")
    BUYOUT_SOURCE_INPUT  = "input[name='buyoutDetails.0.lenderId']"
    BUYOUT_AMOUNT        = "input[name='buyoutDetails.0.buyoutAmount']"

    FIN_INST_SELECT = (
        "//label[normalize-space()='Financial Institution']"
        "/following::div[@role='combobox'][1]"
    )
    SEC_FIN_INST_SELECT = (
        "//label[normalize-space()='Secondary Financial Institution']"
        "/following::div[@role='combobox'][1]"
    )

    # Validation
    FIELD_ERROR    = "p.MuiFormHelperText-root.Mui-error"
    SNACKBAR_ALERT = "[role='alert']"

    # Drafts
    DRAFT_ROW      = "tbody tr"
    NO_DRAFTS_TEXT = "No drafts found"

    def __init__(self, page: Page):
        super().__init__(page)

    # =========================================================================
    # Navigation
    # =========================================================================

    @allure.step("Go to Add Deal page (New Client mode)")
    def goto(self):
        self.page.goto("/add-client?type=new-client")
        self.page.wait_for_selector(self.FIRST_NAME, state="visible", timeout=LONG_TIMEOUT)

    @allure.step("Select New Client mode")
    def select_new_client_mode(self):
        if "type=new-client" not in self.page.url:
            self.page.goto("/add-client?type=new-client")
        self.page.wait_for_selector(self.FIRST_NAME, state="visible", timeout=DEFAULT_TIMEOUT)

    @allure.step("Select Existing Client mode")
    def select_existing_client_mode(self):
        self.page.get_by_label(self.MODE_EXISTING_CLIENT, exact=True).check()
        self.wait_for_network_idle()

    @allure.step("Select Drafts mode")
    def select_drafts_mode(self):
        self.page.get_by_text("Drafts", exact=True).click()
        self.wait_for_timeout(1000)

    # =========================================================================
    # Step navigation
    # =========================================================================

    @allure.step("Click Next: Step 1 -> Step 2 (Lead Details)")
    def click_next_step1(self):
        self.page.locator("(//button[normalize-space()='Next'])[1]").click()
        self.page.wait_for_selector(self.BROKERAGE_SELECT, state="visible", timeout=LONG_TIMEOUT)

    @allure.step("Click Next: Step 2 -> Step 3 (Funding Details)")
    def click_next_step2(self):
        self.page.locator("(//button[normalize-space()='Next'])[2]").click()
        self.page.wait_for_selector(self.FUNDING_AMOUNT, state="visible", timeout=LONG_TIMEOUT)

    def click_next(self):
        self.page.get_by_role("button", name="Next").first.click()

    # =========================================================================
    # AUTO-FILL strategy
    # =========================================================================

    @allure.step("Auto-fill Step 1 (Client Details) via Fill Test Data")
    def fill_client_details_auto(self):
        btn = self.page.locator("(//button[normalize-space()='Fill Test Data'])[1]")
        btn.wait_for(state="visible", timeout=LONG_TIMEOUT)
        btn.click()
        self._wait_for_next1_enabled()

    @allure.step("Open Lead Details and read the Brokerage dropdown options")
    def get_brokerage_options(self) -> list[str]:
        """Reach Step 2 and return the 'Select the Brokerage' dropdown option texts."""
        self.fill_client_details_auto()
        self.click_next_step1()
        self.page.locator(self.BROKERAGE_SELECT).click()
        self.page.wait_for_timeout(700)
        opts = [o.inner_text().strip()
                for o in self.page.get_by_role("option").all() if o.is_visible()]
        self.page.keyboard.press("Escape")
        return [o for o in opts if o]

    @allure.step("Auto-fill Step 2 (Lead Details) via Fill Test Data")
    def fill_lead_details_auto(self):
        btn = self.page.locator("(//button[normalize-space()='Fill Test Data'])[2]")
        btn.wait_for(state="visible", timeout=LONG_TIMEOUT)
        btn.click()
        self._wait_for_next2_enabled()

    @allure.step("Auto-fill Step 3 (Funding Details) via Fill Test Data")
    def fill_funding_details_auto(self):
        btn = self.page.locator("(//button[normalize-space()='Fill Test Data'])[3]")
        btn.wait_for(state="visible", timeout=LONG_TIMEOUT)
        btn.scroll_into_view_if_needed()
        btn.click()
        self.page.wait_for_timeout(3000)

    @allure.step("Mark deal as Buyout and fill Buyout Source + Amount")
    def fill_buyout_details_auto(self, amount: str = "5000"):
        """
        The form requires the Buyout block to be satisfied before Submit enables,
        even though 'Is this a Buyout Deal?' defaults to No. Select Yes, pick the
        first Buyout Source (lender) option, and enter a positive Buyout Amount.
        """
        yes = self.page.locator(self.BUYOUT_YES_RADIO).first
        yes.wait_for(state="attached", timeout=DEFAULT_TIMEOUT)
        if not yes.is_checked():
            yes.click(force=True)
        # Buyout Source (lender) — MUI select rendered after Yes is chosen
        source = self.page.locator(self.BUYOUT_SOURCE_BOX)
        source.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        source.click()
        self.page.locator("[role='option']").first.click()
        # Buyout Amount must be > 0
        amt = self.page.locator(self.BUYOUT_AMOUNT)
        amt.click()
        amt.press("Control+a")
        amt.fill(amount)
        amt.press("Tab")
        self.page.wait_for_timeout(500)

    @allure.step("Auto-fill Deal Documents via Fill Test Documents")
    def fill_deal_documents_auto(self):
        """
        Deal Documents is required (*); Submit stays disabled until documents are
        attached. Clicks the Fill Test Documents button then waits up to 30 s for
        Submit to become enabled (the upload is an async API call).
        """
        btn = self.page.get_by_role("button", name="Fill Test Documents").first
        btn.wait_for(state="visible", timeout=LONG_TIMEOUT)
        btn.scroll_into_view_if_needed()
        btn.click()
        self.page.wait_for_function(
            "() => {"
            "  const b = [...document.querySelectorAll('button')]"
            "    .find(el => el.textContent.trim() === 'Submit');"
            "  return b && !b.disabled;"
            "}",
            timeout=30000,
        )

    # =========================================================================
    # MANUAL-FILL strategy — Step 1: Client Details
    # =========================================================================

    @allure.step("Manually fill Step 1: Client Details")
    def fill_client_details_manually(
        self,
        first_name:           str = "ARYA",
        last_name:            str = "SJ",
        email:                str = "testuser@example.com",
        phone:                str = "9880545476",
        own_home:             str = "Own",
        home_address:         str = "123 Maple Street, Vancouver",
        id_type:              str = "Driving License",
        id_number:            str = "123456879",
        id_expiry_months_fwd: int = 6,
        sin:                  str = "123456789",
        dob_year:             str = "1997",
        dob_month:            str = "August",
        dob_day:              str = "12",
        credit_score:         str = "- 500",
        legal_biz_name:       str = "TEST CORP",
        corp_number:          str = "6575",
        corp_type:            str = "Sole Proprietorship",
        doing_business_as:    str = "TEST DBA",
        industry:             str = "Auto",
        business_city:        str = "Vancouver",
        business_street:      str = "456 Business Ave",
        business_postal:      str = "V6B1A1",
        business_province:    str = "British Columbia",
        avg_monthly_revenue:  str = "10000",
        ownership_pct:        str = "100",
    ):
        self.page.locator(self.FIRST_NAME).fill(first_name)
        self.page.locator(self.LAST_NAME).fill(last_name)
        self.page.locator(self.EMAIL).fill(email)

        phone_el = self.page.locator(self.PHONE)
        phone_el.click()
        phone_el.press("Control+a")
        self.page.keyboard.type(phone)

        self.page.locator(self.OWN_HOME_SELECT).click()
        self.page.get_by_role("option", name=own_home, exact=True).click()

        self.page.locator(self.HOME_ADDRESS).fill(home_address)

        self.page.locator(self.ID_TYPE_SELECT).click()
        self.page.get_by_role("option", name=id_type, exact=True).click()
        self.page.wait_for_timeout(300)

        id_num_el = self.page.locator(self.ID_NUMBER)
        id_num_el.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
        id_num_el.fill(id_number)

        self._pick_expiry_date(id_expiry_months_fwd)

        sin_el = self.page.locator(self.SIN)
        sin_el.click()
        sin_el.press("Control+a")
        self.page.keyboard.type(sin)

        self._pick_dob(dob_year, dob_month, dob_day)

        self.page.locator(self.CREDIT_SCORE_SELECT).click()
        self.page.get_by_role("option", name=credit_score).click()

        self.page.locator(self.LEGAL_BUSINESS_NAME).fill(legal_biz_name)
        self.page.locator(self.CORPORATION_NUMBER).fill(corp_number)

        self.page.locator(self.CORP_TYPE_SELECT).click()
        self.page.get_by_role("option", name=corp_type, exact=True).click()

        self.page.locator(self.DOING_BUSINESS_AS).fill(doing_business_as)

        self.page.locator(self.INDUSTRY_SELECT).click()
        self.page.get_by_role("option", name=industry, exact=True).click()

        self.page.locator(self.BUSINESS_CITY).fill(business_city)
        self.page.locator(self.BUSINESS_STREET).fill(business_street)
        self.page.locator(self.BUSINESS_POSTAL_CODE).fill(business_postal)

        self.page.locator(self.BIZ_PROVINCE_SELECT).click()
        self.page.get_by_role("option", name=business_province, exact=True).click()

        self.page.locator(self.AVG_MONTHLY_REVENUE).fill(avg_monthly_revenue)
        self.page.locator(self.OWNERSHIP_PCT).fill(ownership_pct)

    # =========================================================================
    # MANUAL-FILL strategy — Step 2: Lead Details
    # =========================================================================

    @allure.step("Manually fill Step 2: Lead Details")
    def fill_lead_details_manually(
        self,
        brokerage:         str = "Appruvo Capital - Brokerage",
<<<<<<< HEAD
        underwriter:       str = "None",
=======
        underwriter:       str = None,
>>>>>>> cd899ac3ad04125b6ba0a3d49432655883356fbc
        merchant_call_by:  str = "Aaron C",
        broker_commission: str = "4",
    ):
        self.page.locator(self.BROKERAGE_SELECT).click()
        self.page.get_by_role("option", name=brokerage).click()

        self.page.locator(self.UNDERWRITER_SELECT).click()
        if underwriter:
            self.page.get_by_role("option", name=underwriter).click()
        else:
            self.page.locator("[role='option']").first.click()

        self.page.locator(self.MERCHANT_CALL_SELECT).click()
        self.page.get_by_role("option", name=merchant_call_by).click()

        comm = self.page.locator(self.BROKER_COMMISSION)
        comm.click()
        comm.press("Control+a")
        comm.fill(broker_commission)

    # =========================================================================
    # MANUAL-FILL strategy — Step 3: Funding Details
    # =========================================================================

    @allure.step("Manually fill Step 3: Funding Details")
    def fill_funding_details_manually(
        self,
<<<<<<< HEAD
        financial_institution: str = "None",
=======
        financial_institution: str = None,
>>>>>>> cd899ac3ad04125b6ba0a3d49432655883356fbc
        institution_number:    str = "001",
        transit_number:        str = "12376",
        account_number:        str = "56656365",
        sec_transit_number:    str = "61276",
        sec_account_number:    str = "6126776",
        funding_amount:        str = "20000",
        factor_rate:           str = "1.4",
        payment_amount:        str = "180",
        payment_frequency:     str = "DAILY",
        select_sec_fin_inst:   bool = False,
    ):
        self.page.locator(self.FIN_INST_SELECT).click()
        if financial_institution:
            self.page.get_by_role("option", name=financial_institution).click()
        else:
            self.page.locator("[role='option']").first.click()

        self.page.locator(self.INSTITUTION_NUMBER).fill(institution_number)
        self.page.locator(self.TRANSIT_NUMBER).fill(transit_number)
        self.page.locator(self.ACCOUNT_NUMBER).fill(account_number)

        if select_sec_fin_inst:
            sec_fi = self.page.locator(self.SEC_FIN_INST_SELECT)
            sec_fi.wait_for(state="visible", timeout=DEFAULT_TIMEOUT)
            sec_fi.click()
            self.page.locator("[role='option']").first.click()

        self.page.locator(self.SEC_TRANSIT_NUMBER).fill(sec_transit_number)
        self.page.locator(self.SEC_ACCOUNT_NUMBER).fill(sec_account_number)
        self.page.locator(self.FUNDING_AMOUNT).fill(funding_amount)
        self.page.locator(self.FACTOR_RATE).fill(factor_rate)
        self.page.locator(self.PAYMENT_AMOUNT).fill(payment_amount)

        freq_css = (
            self.PAYMENT_FREQ_WEEKLY
            if payment_frequency.upper() == "WEEKLY"
            else self.PAYMENT_FREQ_DAILY
        )
        radio = self.page.locator(freq_css)
        if not radio.is_checked():
            radio.evaluate("el => el.click()")

    # =========================================================================
    # Complete end-to-end flows
    # =========================================================================

    @allure.step("Complete full deal flow using Fill Test Data (all 3 steps + documents)")
    def complete_full_flow_auto(self):
        self.fill_client_details_auto()
        self.click_next_step1()
        self.fill_lead_details_auto()
        self.click_next_step2()
        self.fill_funding_details_auto()
        self.fill_deal_documents_auto()

    @allure.step("Complete full deal flow using manual form entry (all 3 steps)")
    def complete_full_flow_manually(self, **overrides):
        _client = {
            "first_name", "last_name", "email", "phone", "own_home",
            "home_address", "id_type", "id_number", "id_expiry_months_fwd",
            "sin", "dob_year", "dob_month", "dob_day", "credit_score",
            "legal_biz_name", "corp_number", "corp_type", "doing_business_as",
            "industry", "business_city", "business_street", "business_postal",
            "business_province", "avg_monthly_revenue", "ownership_pct",
        }
        _lead = {"brokerage", "underwriter", "merchant_call_by", "broker_commission"}
        _funding = {
            "financial_institution", "institution_number", "transit_number",
            "account_number", "sec_transit_number", "sec_account_number",
            "funding_amount", "factor_rate", "payment_amount",
            "payment_frequency", "select_sec_fin_inst",
        }
        self.fill_client_details_manually(**{k: v for k, v in overrides.items() if k in _client})
        self.click_next_step1()
        self.fill_lead_details_manually(**{k: v for k, v in overrides.items() if k in _lead})
        self.click_next_step2()
        self.fill_funding_details_manually(**{k: v for k, v in overrides.items() if k in _funding})

    # =========================================================================
    # Submission and confirmation
    # =========================================================================

    @allure.step("Click Submit button")
    def submit(self):
        self.page.get_by_role("button", name="Submit").click()
        self.wait_for_network_idle()

    @allure.step("Click Create button (confirmation dialog)")
    def click_create(self):
        self.page.get_by_role("button", name="Create").click()

    @allure.step("Save form as Draft")
    def save_draft(self):
        btn = self.page.get_by_role("button", name="Save as Draft").first
        btn.wait_for(state="visible")
        btn.click()
        try:
            modal = self.page.locator(".MuiModal-root").last
            confirm = modal.get_by_role("button", name="Save as Draft")
            confirm.wait_for(state="visible", timeout=3000)
            confirm.click()
            modal.wait_for(state="hidden", timeout=10000)
        except Exception:
            pass
        self.wait_for_network_idle()

    def is_deal_created_confirmation_displayed(self) -> bool:
        success = self.page.locator(
            "//*[contains(text(),'success') or contains(text(),'Success') "
            "or contains(text(),'created') or contains(text(),'Created')] "
            "| //*[contains(@class,'MuiSnackbar') or contains(@class,'MuiAlert-success')]"
        ).first
        try:
            success.wait_for(state="attached", timeout=DEFAULT_TIMEOUT)
            return True
        except Exception:
            return self.page.get_by_role("button", name="Create").count() == 0

    # =========================================================================
    # Validation helpers
    # =========================================================================

    @allure.step("Get all inline field validation error texts")
    def get_validation_errors(self) -> list:
        errors = self.page.locator(self.FIELD_ERROR)
        return [errors.nth(i).inner_text() for i in range(errors.count())]

    @allure.step("Assert validation errors are present (inline or snackbar)")
    def assert_has_validation_errors(self):
        inline   = self.page.locator(self.FIELD_ERROR)
        snackbar = self.page.locator(self.SNACKBAR_ALERT)
        try:
            inline.first.wait_for(state="visible", timeout=4000)
        except Exception:
            snackbar.first.wait_for(state="visible", timeout=4000)

    # =========================================================================
    # Dropdown / calculated field helpers
    # =========================================================================

    @allure.step("Open Industry dropdown and count available options")
    def count_select_options(self, label: str) -> int:
        self.page.locator(
            "//label[contains(text(),'Industry')]/following::div[@role='combobox'][1]"
        ).click()
        self.page.wait_for_timeout(800)
        count = self.page.locator("[role='option']").count()
        self.page.keyboard.press("Escape")
        return count

    def select_by_label(self, label: str, option: str):
        self.page.get_by_role("combobox", name=label).click()
        self.page.get_by_role("option", name=option).click()

    def get_calculated_value(self, field_name: str) -> str:
        mapping = {
            "cost_of_borrowing": self.COST_OF_BORROWING,
            "total_payable":     self.TOTAL_PAYABLE,
            "amount_credited":   self.AMOUNT_CREDITED,
            "payment_amount":    self.PAYMENT_AMOUNT,
        }
        return self.page.locator(mapping[field_name]).input_value().strip()

    # =========================================================================
    # Drafts helpers
    # =========================================================================

    def get_draft_count(self) -> int:
        self.select_drafts_mode()
        self.page.wait_for_timeout(1500)
        if self.page.get_by_text(self.NO_DRAFTS_TEXT, exact=False).is_visible():
            return 0
        return self.page.locator(self.DRAFT_ROW).count()

    # =========================================================================
    # Existing client helpers
    # =========================================================================

    def search_existing_client(self, name: str):
        self.select_existing_client_mode()
        self.page.get_by_placeholder("Search").fill(name)
        self.wait_for_network_idle()
        self.page.get_by_role("option", name=name).first.click()

    # =========================================================================
    # Private helpers
    # =========================================================================

    def _wait_for_next1_enabled(self):
        self.page.wait_for_function(
            "() => {"
            "  const b = document.evaluate("
            "    \"(//button[normalize-space()='Next'])[1]\","
            "    document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null"
            "  ).singleNodeValue;"
            "  return b && !b.disabled;"
            "}",
            timeout=LONG_TIMEOUT,
        )

    def _wait_for_next2_enabled(self):
        self.page.wait_for_function(
            "() => {"
            "  const b = document.evaluate("
            "    \"(//button[normalize-space()='Next'])[2]\","
            "    document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null"
            "  ).singleNodeValue;"
            "  return b && !b.disabled;"
            "}",
            timeout=LONG_TIMEOUT,
        )

    def _pick_expiry_date(self, months_ahead: int = 6):
        self.page.get_by_role("button", name="Choose date").first.click()
        self.page.wait_for_timeout(400)
        for _ in range(months_ahead):
            self.page.get_by_role("button", name="Next month").click()
            self.page.wait_for_timeout(150)
        self.page.get_by_role("gridcell", name="10").first.click()

    def _pick_dob(self, year: str = "1997", month: str = "August", day: str = "12"):
        choose_btns = self.page.get_by_role("button", name="Choose date")
        btn_count = choose_btns.count()
        dob_btn = choose_btns.nth(1) if btn_count > 1 else choose_btns.first
        dob_btn.click()
        self.page.wait_for_timeout(400)

        switched = False
        for label in [
            "calendar view is open, switch to year view",
            "calendar view is open, switch",
        ]:
            btn = self.page.get_by_role("button", name=label)
            if btn.count() > 0:
                btn.first.click()
                switched = True
                self.page.wait_for_timeout(300)
                break

        if not switched:
            fallback = self.page.locator("button[aria-label*='switch']").first
            if fallback.is_visible():
                fallback.click()
                self.page.wait_for_timeout(300)

        year_radio = self.page.get_by_role("radio", name=year)
        if year_radio.count() > 0:
            year_radio.click()
            self.page.wait_for_timeout(200)

        month_radio = self.page.get_by_role("radio", name=month)
        if month_radio.count() > 0:
            month_radio.click()
            self.page.wait_for_timeout(200)

<<<<<<< HEAD
        self.page.get_by_role("gridcell", name=day).first.click()
=======
        self.page.get_by_role("gridcell", name=day).first.click()
>>>>>>> cd899ac3ad04125b6ba0a3d49432655883356fbc
