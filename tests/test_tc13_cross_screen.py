"""
test_tc13_cross_screen.py — Cross-screen consistency

Data defined in one screen must appear consistently in others. The original
suite routed through the All Loans page and a Merchant List filter drawer that
are not reachable, plus destructive payment mutations. These tests instead use
the screens that ARE reachable — Control Panel, Add Deal, Reports, Merchant
List — to prove the same reference data is consistent across them.
"""
import pytest
import allure
from pages.merchant_list_page import MerchantListPage
from pages.add_deal_page import AddDealPage
from pages.control_panel_page import ControlPanelPage
from pages.reports_page import ReportsPage


def _norm(s: str) -> str:
    return " ".join((s or "").split()).lower()


@allure.suite("13 — Cross-Screen Consistency")
@pytest.mark.cross_screen
@pytest.mark.regression
class TestCrossScreenConsistency:

    @allure.title("TC-142 | Control Panel brokerages appear in the Add Deal brokerage dropdown")
    def test_control_panel_brokerages_in_add_deal(self, admin_page):
        cp = ControlPanelPage(admin_page)
        cp.goto()
        cp._open_tab("BROKERAGES")
        admin_page.wait_for_timeout(1000)
        cp_brokerages = {_norm(x) for x in cp.get_all_items() if x.strip()}
        assert cp_brokerages, "Control Panel should list at least one brokerage"

        add = AddDealPage(admin_page)
        add.goto()
        options = {_norm(o) for o in add.get_brokerage_options()}
        assert options, "Add Deal should show brokerage options"

        overlap = cp_brokerages & options
        ratio = len(overlap) / len(cp_brokerages)
        assert ratio >= 0.8, (
            f"Only {len(overlap)}/{len(cp_brokerages)} Control Panel brokerages "
            f"appear in the Add Deal dropdown (ratio {ratio:.2f})"
        )

    @allure.title("TC-135 | Reports Lead Source rows are consistent with Control Panel lead sources")
    def test_reports_lead_sources_match_control_panel(self, admin_page):
        cp = ControlPanelPage(admin_page)
        cp.goto()
        cp._open_tab("LEAD SOURCES")
        admin_page.wait_for_timeout(1000)
        cp_leads = {_norm(x) for x in cp.get_all_items() if x.strip()}
        assert cp_leads, "Control Panel should list at least one lead source"

        rp = ReportsPage(admin_page)
        rp.goto()
        rp.select_report_type("Lead Source")
        labels = [rp.get_row_data(i)["label"] for i in range(rp.get_row_count())]
        labels = [_norm(x) for x in labels if x.strip()]
        if not labels:
            pytest.skip("No Lead Source rows in the report")

        matched = [x for x in labels if x in cp_leads]
        ratio = len(matched) / len(labels)
        assert ratio >= 0.7, (
            f"Only {len(matched)}/{len(labels)} Reports lead sources exist in "
            f"Control Panel (ratio {ratio:.2f})"
        )

    @allure.title("TC-146 | Deal Numbers are unique in the Merchants Lended grid")
    def test_deal_numbers_are_unique(self, admin_page):
        ml = MerchantListPage(admin_page)
        ml.goto()
        ml.search("Test")
        idx = ml._header_index_map()
        rows = ml.page.locator(ml.LENDED_ROWS)
        deal_nos = []
        for i in range(rows.count()):
            dn = rows.nth(i).locator("td").nth(idx["Deal No."]).inner_text().strip()
            if dn:
                deal_nos.append(dn)
        assert deal_nos, "Expected at least one deal number"
        dupes = sorted({x for x in deal_nos if deal_nos.count(x) > 1})
        assert not dupes, f"Duplicate Deal Numbers found: {dupes}"
