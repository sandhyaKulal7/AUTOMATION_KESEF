import os
from playwright.sync_api import sync_playwright

env = {}
with open('.env', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k] = v
BASE_URL = env.get('BASE_URL', 'https://kesef.qa.codezyng.com/')
EMAIL = env['TEST_EMAIL']
PASSWORD = env['TEST_PASSWORD']

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(base_url=BASE_URL, viewport={'width': 1920, 'height': 1080})
    page = ctx.new_page()
    page.goto('/', wait_until='networkidle', timeout=30000)
    page.locator("//input[@name='email']").fill(EMAIL)
    page.locator("//input[@name='password']").fill(PASSWORD)
    page.locator("//button[text()='Sign In']").click()
    page.wait_for_url('**/client-portal', timeout=20000)
    page.wait_for_load_state('networkidle', timeout=20000)
    page.goto('/add-client?type=new-client', wait_until='networkidle', timeout=30000)
    page.wait_for_selector("//input[@name='firstName']", timeout=20000)
    page.locator("(//button[normalize-space()='Fill Test Data'])[1]").click()
    page.wait_for_timeout(2000)
    page.locator("(//button[normalize-space()='Next'])[1]").click()
    page.wait_for_selector("//div[@id='mui-component-select-brokerageId']", timeout=20000)
    page.locator("(//button[normalize-space()='Fill Test Data'])[2]").click()
    page.wait_for_timeout(2000)
    page.locator("(//button[normalize-space()='Next'])[2]").click()
    page.wait_for_selector("//input[@name='fundingAmount']", timeout=20000)
    page.locator("(//button[normalize-space()='Fill Test Data'])[3]").click()
    page.wait_for_timeout(3000)

    def log(name, value):
        print(f"--- {name} ---")
        print(value)

    def field_state(name):
        return page.evaluate(
            "name => { const input = document.querySelector(`input[name=\'${name}\']`); if (!input) return null; const root = input.closest('div.MuiFormControl-root'); return {name: name, value: input.value, ariaInvalid: input.getAttribute('aria-invalid'), ariaDescribedBy: input.getAttribute('aria-describedby'), className: input.className, rootClass: root ? root.className : null, rootErrs: root ? Array.from(root.querySelectorAll('p,span,div')).filter(el => el.textContent.trim()).map(el => ({tag: el.tagName, className: el.className, text: el.textContent.trim()})) : []}; }",
            name,
        )

    def errors_text(term):
        return page.evaluate(
            "term => Array.from(document.querySelectorAll('*')).filter(el => el.textContent && el.textContent.toLowerCase().includes(term.toLowerCase())).map(el => ({tag: el.tagName, className: el.className, text: el.textContent.trim()})).slice(0,20)",
            term,
        )

    def helper_errors():
        return page.evaluate(
            "() => Array.from(document.querySelectorAll('p.MuiFormHelperText-root, span.MuiFormHelperText-root, div.MuiFormHelperText-root')).map(el => ({tag: el.tagName, className: el.className, text: el.textContent.trim()})).slice(0,40)"
        )

    def dispatch_to_field(name, value):
        page.evaluate(
            "(name, value) => { const input = document.querySelector(`input[name=\\'${name}\\']`); if(!input) return false; input.focus(); input.value = value; input.dispatchEvent(new Event('input', {bubbles: true})); input.dispatchEvent(new Event('change', {bubbles: true})); input.dispatchEvent(new Event('blur', {bubbles: true})); return true; }",
            name,
            value,
        )
        page.wait_for_timeout(1200)

    log('step3 field states before', {'factorRate': field_state('factorRate'), 'fundingAmount': field_state('fundingAmount')})
    log('helper texts before', helper_errors())

    # Clear factorRate using JS events
    dispatch_to_field('factorRate', '')
    log('factorRate after JS clear', field_state('factorRate'))
    log('helper texts after factorRate clear', helper_errors())
    log('factorRate text matches', errors_text('Factor Rate is required'))

    # Set fundingAmount to 0 using JS events
    dispatch_to_field('fundingAmount', '0')
    log('fundingAmount after JS 0', field_state('fundingAmount'))
    log('helper texts after fundingAmount set 0', helper_errors())
    log('fundingAmount text matches', errors_text('Funding Amount must be greater than zero'))

    # Force submit if possible
    if page.locator("button:has-text('Submit')").count() > 0:
        page.locator("button:has-text('Submit')").click(force=True)
        page.wait_for_timeout(2000)
        log('after submit helper texts', helper_errors())
        log('after submit greater than zero', errors_text('greater than zero'))
        log('after submit factor rate required', errors_text('factor rate is required'))

    browser.close()
