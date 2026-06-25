"""
dashboard_page.py — Dashboard page object
"""
import re
import allure
from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class DashboardPage(BasePage):
    MONTHLY_FUNDED_CHART  = "[data-testid='chart-monthly-funded']"
    INDUSTRY_CHART        = "[data-testid='chart-industry']"
    PROVINCE_MAP          = "[data-testid='chart-province-map']"
    NEW_VS_RENEWAL_CHART  = "[data-testid='chart-new-vs-renewal']"
    KPI_FUNDED            = "[data-testid='kpi-total-funded']"
    KPI_ACTIVE            = "[data-testid='kpi-active-deals']"
    KPI_COLLECTED         = "[data-testid='kpi-total-collected']"
    KPI_DEFAULT_RATE      = "[data-testid='kpi-default-rate']"

    def __init__(self, page: Page):
        super().__init__(page)

    @allure.step("Go to Dashboard")
    def goto(self):
        self.page.goto("/dashboard")
        self.wait_for_network_idle()

    @allure.step("Get KPI: total funded")
    def get_total_funded(self) -> float:
        raw = self.page.locator(self.KPI_FUNDED).inner_text()
        return float(re.sub(r"[^\d.]", "", raw) or "0")

    @allure.step("Assert dashboard KPIs visible")
    def assert_kpis_visible(self):
        for kpi in [self.KPI_FUNDED, self.KPI_ACTIVE, self.KPI_COLLECTED]:
            expect(self.page.locator(kpi)).to_be_visible()

    @allure.step("Assert chart visible: {chart_name}")
    def assert_chart_visible(self, chart_name: str):
        mapping = {
            "monthly_funded": self.MONTHLY_FUNDED_CHART,
            "industry":       self.INDUSTRY_CHART,
            "province":       self.PROVINCE_MAP,
            "new_vs_renewal": self.NEW_VS_RENEWAL_CHART,
        }
        expect(self.page.locator(mapping[chart_name])).to_be_visible()
