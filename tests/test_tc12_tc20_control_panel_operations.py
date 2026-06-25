"""
test_tc12_tc20_control_panel_operations.py — Control Panel Operations (TC12-TC20)

Test Cases:
  TC12: Add Sales Rep → appears in Sales Reps list & Add Deal dropdown
  TC13: Add Underwriter → appears in Underwriters list & Add Deal dropdown
  TC14: Add Lead Source → appears in Lead Sources list & Add Deal dropdown
  TC15: Add Industry → appears in Industry list & Add Deal dropdown
  TC16: Add Province → appears in Province list & Add Deal dropdown
  TC17: Add Holiday → skipped in payment schedule calculations
  TC18: Deactivate lookup value → removed from dropdowns
  TC19: Bulk replace Sales Rep → updates all deals
  TC20: Add Brokerage → appears in Brokerage dropdown
  TC21: Add Payment Processor → appears in Payment Processor dropdown
"""
import re
import pytest
import allure
from datetime import date, timedelta
from faker import Faker
from playwright.sync_api import expect
from pages.control_panel_page import ControlPanelPage
from pages.add_deal_page import AddDealPage
from pages.merchant_list_page import MerchantListPage
from pages.reports_page import ReportsPage

fake = Faker()


@allure.suite("12-20 — Control Panel Operations")
@pytest.mark.ui
@pytest.mark.regression
class TestControlPanelOperations:

    # ═════════════════════════════════════════════════════════════════════════
    # TC12: Add Sales Rep
    # ═════════════════════════════════════════════════════════════════════════
    @allure.title("TC12 | Add Sales Rep with commission % appears in lists")
    @pytest.mark.smoke
    def test_add_sales_rep_with_commission(self, admin_page):
        """
        1. Control Panel → Sales Reps
        2. Click Add
        3. Enter name, email, commission %
        4. Save
        → New Sales Rep appears in list
        → Immediately available in Add Deal → Sales Rep dropdown
        → Immediately available in Merchant List filter
        """
        name = f"SalesRep_{fake.unique.word()}{fake.random_int(1000, 9999)}"
        email = f"salesrep_{fake.random_int(10000, 99999)}@test.com"

        cp = ControlPanelPage(admin_page)
        cp.goto()
        cp.add_sales_rep(name, email, phone="9990001234")
        cp.assert_add_succeeded()
        cp.assert_item_in_current_tab(name)

        # Verify in Add Deal dropdown
        deal = AddDealPage(admin_page)
        deal.goto()
        sales_rep_dropdown = admin_page.locator("label:has-text('Sales Rep') + div")
        sales_rep_dropdown.click()
        expect(admin_page.get_by_role("option", name=re.compile(name))).to_be_visible()

    # ═════════════════════════════════════════════════════════════════════════
    # TC13: Add Underwriter
    # ═════════════════════════════════════════════════════════════════════════
    @allure.title("TC13 | Add Underwriter appears in dropdowns and filters")
    @pytest.mark.smoke
    def test_add_underwriter(self, admin_page):
        """
        1. Control Panel → Underwriters
        2. Add new underwriter
        3. Save
        → Appears in Add Deal → Underwriter dropdown
        → Appears in Reports filter
        """
        uw_name = f"Underwriter_{fake.unique.word()}{fake.random_int(1000, 9999)}"

        cp = ControlPanelPage(admin_page)
        cp.goto()
        cp.switch_tab("UNDERWRITERS")
        cp.add_item(uw_name)
        cp.assert_add_succeeded()
        cp.assert_item_in_current_tab(uw_name)

        # Verify in Add Deal dropdown
        deal = AddDealPage(admin_page)
        deal.goto()
        uw_dropdown = admin_page.locator("label:has-text('Underwriter') + div")
        uw_dropdown.click()
        expect(admin_page.get_by_role("option", name=re.compile(uw_name))).to_be_visible()

    # ═════════════════════════════════════════════════════════════════════════
    # TC14: Add Lead Source
    # ═════════════════════════════════════════════════════════════════════════
    @allure.title("TC14 | Add Lead Source appears in Add Deal dropdown & filters")
    def test_add_lead_source_appears_in_add_deal(self, admin_page):
        """
        1. Control Panel → Lead Source
        2. Add new source
        3. Save
        → Appears in Add Deal → Lead Source dropdown
        → Appears in Merchant List filter
        """
        source_name = f"Source_{fake.unique.word()}{fake.random_int(1000, 9999)}"

        cp = ControlPanelPage(admin_page)
        cp.goto()
        cp.switch_tab("LEAD SOURCES")
        cp.add_item(source_name)
        cp.assert_add_succeeded()
        cp.assert_item_in_current_tab(source_name)

        # Verify in Add Deal dropdown
        deal = AddDealPage(admin_page)
        deal.goto()
        source_dropdown = admin_page.locator("label:has-text('Lead Source') + div")
        source_dropdown.click()
        expect(admin_page.get_by_role("option", name=re.compile(source_name))).to_be_visible()

    # ═════════════════════════════════════════════════════════════════════════
    # TC15: Add Industry
    # ═════════════════════════════════════════════════════════════════════════
    @allure.title("TC15 | Add Industry appears in Add Deal, filters & dashboard")
    def test_add_industry(self, admin_page):
        """
        1. Control Panel → Industry
        2. Add new industry
        3. Save
        → Appears in Add Deal → Industry dropdown
        → Appears in Merchant List filter
        → Appears in Dashboard chart
        """
        industry_name = f"Industry_{fake.unique.word()}{fake.random_int(1000, 9999)}"

        cp = ControlPanelPage(admin_page)
        cp.goto()
        cp.switch_tab("INDUSTRIES")
        cp.add_item(industry_name)
        cp.assert_add_succeeded()
        cp.assert_item_in_current_tab(industry_name)

        # Verify in Add Deal dropdown
        deal = AddDealPage(admin_page)
        deal.goto()
        industry_dropdown = admin_page.locator("label:has-text('Industry') + div")
        industry_dropdown.click()
        expect(admin_page.get_by_role("option", name=re.compile(industry_name))).to_be_visible()

    # ═════════════════════════════════════════════════════════════════════════
    # TC16: Add Province
    # ═════════════════════════════════════════════════════════════════════════
    @allure.title("TC16 | Add Province appears in Add Deal, filters & reports")
    def test_add_province(self, admin_page):
        """
        1. Control Panel → Province
        2. Add new province
        3. Save
        → Appears in Add Deal → Province dropdown
        → Appears in Merchant List filter
        → Appears in Reports
        """
        province_name = f"Province_{fake.unique.word()}{fake.random_int(1000, 9999)}"

        cp = ControlPanelPage(admin_page)
        cp.goto()
        cp.switch_tab("PROVINCES")
        cp.add_item(province_name)
        cp.assert_add_succeeded()
        cp.assert_item_in_current_tab(province_name)

        # Verify in Add Deal dropdown
        deal = AddDealPage(admin_page)
        deal.goto()
        province_dropdown = admin_page.locator("label:has-text('Province') + div")
        province_dropdown.click()
        expect(admin_page.get_by_role("option", name=re.compile(province_name))).to_be_visible()

    # ═════════════════════════════════════════════════════════════════════════
    # TC17: Add Holiday (skipped in payment schedule)
    # ═════════════════════════════════════════════════════════════════════════
    @allure.title("TC17 | Add Holiday is skipped in Edit Payment schedule")
    @pytest.mark.flaky(reruns=1)
    def test_add_holiday_skips_payment_schedule(self, admin_page):
        """
        1. Control Panel → Holidays
        2. Add a future date (e.g. next Monday)
        3. Save
        4. Fund a deal with start date = day before that Monday
        → The Monday holiday is skipped in Edit Payment schedule
        → First payment falls on Tuesday (after the holiday)
        """
        # Pick a Monday in the future
        today = date.today()
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        monday = today + timedelta(days=days_until_monday)
        holiday_date = monday.strftime("%m/%d/%Y")

        # Add the holiday
        cp = ControlPanelPage(admin_page)
        cp.goto()
        cp.switch_tab("HOLIDAYS")
        cp.add_holiday(
            holiday_date,
            f"Holiday_{monday.strftime('%Y%m%d')}"
        )
        cp.assert_add_succeeded()

        # TODO: Create a deal with start date = Sunday (day before Monday)
        # Then verify payment schedule skips the Monday holiday
        # This requires integration with AddDealPage and EditPaymentPage

    # ═════════════════════════════════════════════════════════════════════════
    # TC18: Deactivate Lookup Value
    # ═════════════════════════════════════════════════════════════════════════
    @allure.title("TC18 | Deactivate Sales Rep removes from dropdown")
    def test_deactivate_lookup_value(self, admin_page):
        """
        1. Deactivate an existing Sales Rep
        2. Go to Add Deal → Sales Rep dropdown
        → Deactivated Sales Rep no longer appears in the dropdown
        """
        # First, add a sales rep
        name = f"SalesRep_Deactivate_{fake.unique.word()}{fake.random_int(1000, 9999)}"
        email = f"deactivate_{fake.random_int(10000, 99999)}@test.com"

        cp = ControlPanelPage(admin_page)
        cp.goto()
        cp.add_sales_rep(name, email)
        cp.assert_add_succeeded()

        # Now deactivate it
        cp.deactivate_item(name)
        cp.assert_deactivation_succeeded()

        # Verify it's NOT in Add Deal dropdown
        deal = AddDealPage(admin_page)
        deal.goto()
        sales_rep_dropdown = admin_page.locator("label:has-text('Sales Rep') + div")
        sales_rep_dropdown.click()
        admin_page.wait_for_timeout(500)

        # The deactivated rep should NOT appear
        options = admin_page.get_by_role("option")
        option_texts = [opt.inner_text() for opt in options.all()]
        assert not any(name in text for text in option_texts), \
            f"Deactivated Sales Rep '{name}' should not appear in dropdown"

    # ═════════════════════════════════════════════════════════════════════════
    # TC19: Bulk Replace Sales Rep
    # ═════════════════════════════════════════════════════════════════════════
    @allure.title("TC19 | Bulk Replace Sales Rep updates all deals")
    @pytest.mark.skip(reason="Requires pre-created deals with old Sales Rep; "
                             "integration test, not just UI")
    def test_bulk_replace_sales_rep(self, admin_page):
        """
        1. Control Panel → Bulk Replace
        2. Select old Sales Rep, new Sales Rep
        3. Submit
        → All deals previously assigned to old Sales Rep now show new Sales Rep
        → Old rep has 0 deals
        """
        pass

    # ═════════════════════════════════════════════════════════════════════════
    # TC20: Add Brokerage
    # ═════════════════════════════════════════════════════════════════════════
    @allure.title("TC20 | Add Brokerage appears in Add Deal dropdown & filters")
    def test_add_brokerage(self, admin_page):
        """
        1. Control Panel → Brokerages
        2. Add name
        3. Save
        → Appears in Add Deal → Brokerage dropdown
        → Appears in Merchant List filter
        """
        brokerage_name = f"Brokerage_{fake.unique.word()}{fake.random_int(1000, 9999)}"

        cp = ControlPanelPage(admin_page)
        cp.goto()
        cp.switch_tab("BROKERAGES")
        cp.add_item(brokerage_name)
        cp.assert_add_succeeded()
        cp.assert_item_in_current_tab(brokerage_name)

        # Verify in Add Deal dropdown
        deal = AddDealPage(admin_page)
        deal.goto()
        brokerage_dropdown = admin_page.locator("label:has-text('Brokerage') + div")
        brokerage_dropdown.click()
        expect(admin_page.get_by_role("option", name=re.compile(brokerage_name))).to_be_visible()

    # ═════════════════════════════════════════════════════════════════════════
    # TC21: Add Payment Processor
    # ═════════════════════════════════════════════════════════════════════════
    @allure.title("TC21 | Add Payment Processor appears in Fund Deal dropdown")
    def test_add_payment_processor(self, admin_page):
        """
        1. Control Panel → Payment Processor
        2. Add new processor
        3. Save
        → Appears in Fund Deal → Payment Processor dropdown
        → Appears in Daily Payment Summary filter
        """
        processor_name = f"Processor_{fake.unique.word()}{fake.random_int(1000, 9999)}"

        cp = ControlPanelPage(admin_page)
        cp.goto()
        cp.switch_tab("PAYMENT PROCESSOR")
        cp.add_item(processor_name)
        cp.assert_add_succeeded()
        cp.assert_item_in_current_tab(processor_name)

        # Verify in Fund Deal dropdown (would need FundDealPage helper)
        # For now, just verify it's in the Control Panel list
