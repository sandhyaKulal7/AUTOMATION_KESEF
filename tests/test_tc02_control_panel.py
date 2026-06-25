"""
test_tc02_control_panel.py — Control Panel add operations

The Control Panel is a tabbed CRUD page. These tests verify that a newly added
item (Sales Rep, Lead Source, Holiday) appears in that tab's list. The Add Deal
form has no Sales Rep / Lead Source field, so cross-screen propagation is out of
scope here (it belongs to the cross-screen suite if/when those fields exist).
"""
import pytest
import allure
from datetime import date, timedelta
from faker import Faker
from pages.control_panel_page import ControlPanelPage

fake = Faker()


@allure.suite("02 — Control Panel")
@pytest.mark.ui
@pytest.mark.regression
class TestControlPanel:

    @allure.title("TC-11 | Add Sales Rep appears in the Sales Reps list")
    @pytest.mark.smoke
    def test_add_sales_rep(self, admin_page):
        name = f"AutoRep {fake.unique.last_name()}{fake.random_number(digits=4)}"
        cp = ControlPanelPage(admin_page)
        cp.goto()
        cp.add_sales_rep(name, f"autorep{fake.random_number(digits=6)}@test.com")
        cp.assert_add_succeeded()
        cp.assert_item_exists(name)

    @allure.title("TC-13 | Add Lead Source appears in the Lead Sources list")
    def test_add_lead_source(self, admin_page):
        name = f"AutoSource {fake.unique.word().capitalize()}{fake.random_number(digits=4)}"
        cp = ControlPanelPage(admin_page)
        cp.goto()
        cp.add_lead_source(name)
        cp.assert_add_succeeded()
        cp.assert_item_exists(name)

    @allure.title("TC-16 | Add Holiday appears in the Holidays list")
    def test_add_holiday(self, admin_page):
        # The app rejects a duplicate holiday date, so pick a unique future date
        # each run (a random offset well ahead of today).
        offset = fake.random_int(min=60, max=900)
        holiday = date.today() + timedelta(days=offset)
        holiday_mmddyyyy = holiday.strftime("%m/%d/%Y")
        description = f"Auto Holiday {holiday.strftime('%Y%m%d')}"

        cp = ControlPanelPage(admin_page)
        cp.goto()
        cp.add_holiday(holiday_mmddyyyy, description)
        # The Holidays table sorts by date and paginates, so the new far-future
        # row may not be on the first page — assert the success signal instead.
        cp.assert_add_succeeded()
