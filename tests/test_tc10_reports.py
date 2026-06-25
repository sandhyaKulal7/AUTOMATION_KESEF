"""
test_tc10_reports.py — Reports page

The Reports page renders a report table automatically when a Report type is
selected (no Generate button, no from/to date inputs, no drill-down modal).
These tests verify report generation for several types and the Excel export.
"""
import pytest
import allure
from pages.reports_page import ReportsPage


@allure.suite("10 — Reports")
@pytest.mark.reports
@pytest.mark.regression
class TestReports:

    @allure.title("TC-112 | Sales Rep report generates")
    def test_sales_rep_report_generates(self, admin_page):
        rp = ReportsPage(admin_page)
        rp.goto()
        rp.select_report_type("Sales Rep")
        assert rp.get_row_count() >= 1, "Sales Rep report should render at least one row"

    @allure.title("TC-119 | KM Capital Book Report generates")
    def test_book_report_generates(self, admin_page):
        rp = ReportsPage(admin_page)
        rp.goto()
        rp.select_report_type("KM Capital Book Report")
        assert rp.get_row_count() >= 1, "Book report should render at least one row"

    @allure.title("TC-121 | Lead Source report rows expose a label and amount")
    def test_lead_source_report_rows(self, admin_page):
        rp = ReportsPage(admin_page)
        rp.goto()
        rp.select_report_type("Lead Source")
        if rp.get_row_count() == 0:
            pytest.skip("No data for Lead Source report")
        row = rp.get_row_data(0)
        assert row["label"] != "", "First row should have a Lead Source label"
        assert row["amount_funded"] >= 0, "Amount Funded should parse to a number"

    @allure.title("TC-124 | Export to Excel downloads an .xlsx file")
    @pytest.mark.smoke
    def test_export_excel(self, admin_page):
        rp = ReportsPage(admin_page)
        rp.goto()
        rp.select_report_type("Sales Rep")
        download = rp.export_to_excel()
        assert download.suggested_filename.endswith(".xlsx"), \
            f"Expected .xlsx file, got {download.suggested_filename}"
