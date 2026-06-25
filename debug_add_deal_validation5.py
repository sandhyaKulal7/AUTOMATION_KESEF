import os
import json
from playwright.sync_api import sync_playwright

env = {}
with open('.env', 'r', encoding='utf-8') as f:
    for line in f:
        line=line.strip()
        if '=' in line and not line.startswith('#'):
            k,v=line.split('=',1); env[k]=v
BASE_URL=env.get('BASE_URL','https://kesef.qa.codezyng.com/')
EMAIL=env['TEST_EMAIL']
PASSWORD=env['TEST_PASSWORD']

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    ctx=browser.new_context(base_url=BASE_URL, viewport={'width':1920,'height':1080})
    page=ctx.new_page()
    page.goto('/', wait_until='networkidle', timeout=30000)
    page.locator("//input[@name='email']").fill(EMAIL)
    page.locator("//input[@name='password']").fill(PASSWORD)
    page.locator("//button[text()='Sign In']").click()
    page.wait_for_url('**/client-portal', timeout=20000)
    page.wait_for_load_state('networkidle', timeout=20000)
    page.goto('/add-client?type=new-client', wait_until='networkidle', timeout=30000)
    page.wait_for_selector("//input[@name='firstName']", state='visible', timeout=20000)

    def dump(label, data):
        print('---', label, '---')
        print(json.dumps(data, indent=2)[:20000])

    def find_text(substr):
        return page.evaluate(
            "substr => Array.from(document.querySelectorAll('*')).filter(el => el.textContent && el.textContent.toLowerCase().includes(substr.toLowerCase())).slice(0,80).map(el => ({tag: el.tagName, className: el.className, text: el.textContent.trim(), outerHTML: el.outerHTML.slice(0,400)}))",
            substr,
        )

    def find_by_selector(selector):
        return page.evaluate(
            "selector => Array.from(document.querySelectorAll(selector)).slice(0,80).map(el => ({tag: el.tagName, className: el.className, text: el.textContent.trim(), outerHTML: el.outerHTML.slice(0,400)}))",
            selector,
        )

    def field_state(name):
        return page.evaluate(
            "name => { const el = document.querySelector(`input[name='${name}']`); if(!el) return null; const root = el.closest('div.MuiFormControl-root'); return {name: name, value: el.value, ariaInvalid: el.getAttribute('aria-invalid'), ariaDescribedBy: el.getAttribute('aria-describedby'), type: el.type, className: el.className, rootClass: root ? root.className : null, rootOuter: root ? root.outerHTML.slice(0,1000) : null, siblingTexts: root ? Array.from(root.querySelectorAll('p,span,div,label')).map(x=>({tag:x.tagName, className:x.className, text:x.textContent.trim().slice(0,200)})) : []}; }",
            name,
        )

    def find_aria_invalid():
        return page.evaluate("() => Array.from(document.querySelectorAll('input[aria-invalid]')).map(el => ({name: el.name, aria: el.getAttribute('aria-invalid'), value: el.value, className: el.className}))")

    def count(selector):
        return page.locator(selector).count()

    dump('step1 initial field errors', find_by_selector('p.MuiFormHelperText-root, span.MuiFormHelperText-root, div.MuiFormHelperText-root, .Mui-error, [role=alert]'))
    page.locator("button:has-text('Next')").first.click()
    page.wait_for_timeout(2000)
    dump('step1 after click next errors', find_by_selector('p.MuiFormHelperText-root, span.MuiFormHelperText-root, div.MuiFormHelperText-root, .Mui-error, [role=alert]'))
    dump('step1 required texts', find_text('required'))
    dump('step1 error texts', find_text('error'))
    dump('step1 field state firstName', field_state('firstName'))
    dump('step1 aria invalid', find_aria_invalid())

    page.locator("(//button[normalize-space()='Fill Test Data'])[1]").click()
    page.wait_for_timeout(2000)
    page.locator("(//button[normalize-space()='Next'])[1]").click()
    page.wait_for_selector("//div[@id='mui-component-select-brokerageId']", state='visible', timeout=20000)
    page.locator("(//button[normalize-space()='Fill Test Data'])[2]").click()
    page.wait_for_timeout(2000)
    page.locator("(//button[normalize-space()='Next'])[2]").click()
    page.wait_for_selector("//input[@name='fundingAmount']", state='visible', timeout=20000)

    dump('step3 field state factorRate pre', field_state('factorRate'))
    dump('step3 field state fundingAmount pre', field_state('fundingAmount'))
    page.locator("input[name='factorRate']").click()
    page.locator("input[name='factorRate']").press('Control+a')
    page.locator("input[name='factorRate']").press('Delete')
    page.locator("input[name='factorRate']").press('Tab')
    page.wait_for_timeout(2000)
    dump('factorRate after clear state', field_state('factorRate'))
    dump('factorRate text required', find_text('Factor Rate is required'))
    dump('aria-invalid inputs after factorRate', find_aria_invalid())
    dump('root siblings factorRate', find_by_selector('input[name="factorRate"] + *'))

    page.locator("input[name='fundingAmount']").click()
    page.locator("input[name='fundingAmount']").press('Control+a')
    page.locator("input[name='fundingAmount']").press('Delete')
    page.keyboard.type('0')
    page.locator("input[name='fundingAmount']").press('Tab')
    page.wait_for_timeout(2000)
    dump('fundingAmount after blur state', field_state('fundingAmount'))
    dump('fundingAmount text', find_text('Funding Amount must be greater than zero'))
    dump('aria-invalid inputs after fundingAmount', find_aria_invalid())
    # Attempt to attach test documents so Submit becomes enabled if form is valid.
    try:
        btn = page.locator("button:has-text('Fill Test Documents')").first
        if btn.count() > 0:
            btn.click()
            page.wait_for_timeout(3000)
    except Exception:
        pass

    submit_btn = page.locator("button:has-text('Submit')").first
    browser_enabled = submit_btn.is_enabled()
    print('submit enabled after docs', browser_enabled)
    try:
        submit_btn.click(force=True)
    except Exception as e:
        print('submit force click failed', str(e))
    page.wait_for_timeout(3000)
    dump('after submit texts greater than zero', find_text('greater than zero'))
    dump('after submit texts factor rate required', find_text('Factor Rate is required'))
    dump('after submit error selectors', find_by_selector('.Mui-error, p.MuiFormHelperText-root, span.MuiFormHelperText-root, div.MuiFormHelperText-root, [role=alert]'))
    browser.close()
