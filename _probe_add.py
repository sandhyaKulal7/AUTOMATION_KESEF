"""Probe /add-client: mode selectors, validation errors, section accordion, MUI selects."""
import os, sys, re
from dotenv import load_dotenv
load_dotenv(".env")

BASE  = os.environ["BASE_URL"].rstrip("/")
EMAIL = os.environ["TEST_EMAIL"]
PWD   = os.environ["TEST_PASSWORD"]

import subprocess, json
result = subprocess.run(
    ["python", "-c", f"""
import sys
sys.path.insert(0, '.')
from playwright.sync_api import sync_playwright

BASE = "{BASE}"
EMAIL = "{EMAIL}"
PWD = "{PWD}"

with sync_playwright() as p:
    br = p.chromium.launch(headless=True)
    ctx = br.new_context(base_url=BASE)
    pg = ctx.new_page()
    pg.goto("/")
    pg.wait_for_selector("input[name='email']", timeout=10000)
    pg.locator("input[name='email']").fill(EMAIL)
    pg.locator("input[name='password']").fill(PWD)
    pg.get_by_role("button", name="Sign In").click()
    pg.wait_for_url("**/client-portal", timeout=20000)

    pg.goto("/add-client", wait_until="networkidle")

    # 1. How are the mode "tabs" (New Client / Existing Client / Drafts) rendered?
    tabs = pg.locator("role=tab").all()
    print("ROLE=TAB count:", len(tabs))
    for t in tabs:
        print("  tab:", repr(t.inner_text()[:60]))

    # Check labels for mode selection
    labels = pg.locator("label").all()
    mode_labels = [l.inner_text().strip() for l in labels if l.inner_text().strip() in ("New Client","Existing Client","Drafts")]
    print("MODE LABELS:", mode_labels)

    # check MUI tab classes
    mui_tabs = pg.locator(".MuiTab-root").all()
    print("MuiTab-root count:", len(mui_tabs))
    for t in mui_tabs:
        print("  MuiTab:", repr(t.inner_text()[:40]))

    # 2. Click Next to trigger validation — what error selector appears?
    pg.get_by_role("button", name="Next").click()
    pg.wait_for_timeout(2000)
    
    # Try common error selectors
    for sel in [
        ".Mui-error",
        "p.MuiFormHelperText-root",
        "[role='alert']",
        "span.error",
        "div.error",
        ".field-error",
        "p[class*='error']",
        "span[class*='error']",
    ]:
        cnt = pg.locator(sel).count()
        if cnt:
            sample = pg.locator(sel).first.inner_text()[:80]
            print(f"ERRORS [{sel}]: count={cnt} sample={repr(sample)}")

    # 3. Check accordion/section headers
    accordions = pg.locator(".MuiAccordion-root, [class*='accordion']").all()
    print("Accordions:", len(accordions))
    
    # 4. Check how 'brokerageId' and 'underwriterId' dropdowns are rendered
    for fname in ["brokerageId", "underwriterId", "merchantCallBy", "ownHome", "idType"]:
        loc = pg.locator(f"[name='{fname}']")
        cnt = loc.count()
        if cnt:
            tag = loc.first.evaluate("el => el.tagName")
            role = loc.first.get_attribute("role") or ""
            aria = loc.first.get_attribute("aria-label") or ""
            print(f"FIELD {fname}: tag={tag} role={role} aria={aria}")

    # 5. What does 'Fill Test Data' do? Get form values after clicking it
    pg.get_by_role("button", name="Fill Test Data").click()
    pg.wait_for_timeout(2000)
    sample_vals = {{}}
    for fname in ["firstName","lastName","clientEmail","clientPhone","fundingAmount","factorRate","numberOfPayments"]:
        loc = pg.locator(f"input[name='{fname}']")
        if loc.count():
            sample_vals[fname] = loc.first.input_value()
    print("FILL TEST DATA sample:", json.dumps(sample_vals))

    # 6. Sales Rep / Lead Source / Brokerage — how to open?
    # Look for their label text
    for label_text in ["Sales Rep", "Lead Source", "Brokerage", "Underwriter"]:
        locs = pg.get_by_text(label_text, exact=False)
        if locs.count():
            print(f"Label '{label_text}' found, count={locs.count()}")

    br.close()
"""],
    capture_output=True, text=True, cwd="."
)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr[-2000:])
