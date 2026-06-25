"""
test_tc08_merchant_list.py — Merchant List ("Merchants Lended") page

The live page supports a client search box and a read-only data grid. It has no
filter drawer (status / sales-rep / date-range filters do not exist in the app),
and grid rows are not navigable, so only the search + row-content cases are
covered here. Test data is whatever already exists under the "Test" clients
seeded by the Add Deal flow, so assertions stay data-independent.
"""
import pytest
import allure
from pages.merchant_list_page import MerchantListPage


@allure.suite("08 — Merchant List")
@pytest.mark.ui
@pytest.mark.regression
class TestMerchantList:

    @allure.title("TC-90 | Search filters the Merchants Lended list")
    def test_search_filters_in_real_time(self, admin_page):
        ml = MerchantListPage(admin_page)
        ml.goto()
        # Grid is empty until a search is entered.
        assert ml.get_row_count() == 0, "List should be empty before searching"
        ml.search("Test")
        assert ml.get_row_count() >= 1, "Searching 'Test' should return at least one row"

    @allure.title("TC-91 | Row columns are populated with deal values")
    def test_row_columns_match_deal(self, admin_page):
        ml = MerchantListPage(admin_page)
        ml.goto()
        ml.search("Test")
        assert ml.get_row_count() >= 1, "Expected at least one matching row"
        data = ml.get_first_row_data()
        assert data["client_name"] != "", "Client Name column should not be empty"
        assert data["deal_no"] != "", "Deal No. column should not be empty"
        assert data["business_name"] != "", "Legal Business Name column should not be empty"
        assert data["status"] != "", "Deal Status column should not be empty"
