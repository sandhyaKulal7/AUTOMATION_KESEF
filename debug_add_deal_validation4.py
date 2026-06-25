import os
from playwright.sync_api import sync_playwright

env = {}
with open('.env', 'r', encoding='utf-8') as f:
    for line in f:
        line=line.strip()
        if '=' in line and not line.startswith('#'):
            k,v=line.split('=',1)
            env[k]=v
BASE_URL=env.get('BASE_URL','https://kesef.qa.codezyng.com/')
EMAIL=env['TEST_EMAIL']
PASSWORD=env['TEST_PASSWORD']

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(base_url=BASE_URL, viewport={'width':1920,'height':1080})
    page = context.new_page()
    page.goto('/', wait_until='networkidle', timeout=30000)
    page.locator("//input[@name='email']").fill(EMAIL)
    page.locator("//input[@name='password']").fill(PASSWORD)
    page.locator("//button[text()='Sign In']").click()
    page.wait_for_url('**/client-portal', timeout=20000)
    page.wait_for_load_state('networkidle', timeout=20000)
    page.goto('/add-client?type=new-client', wait_until='networkidle', timeout=30000)
    page.wait_for_selector("//input[@name='firstName']", state='visible', timeout=20000)
    page.locator("(//button[normalize-space()='Fill Test Data'])[1]").click()
    page.wait_for_timeout(2000)
    page.locator("(//button[normalize-space()='Next'])[1]").click()
    page.wait_for_selector("//div[@id='mui-component-select-brokerageId']", state='visible', timeout=20000)
    page.locator("(//button[normalize-space()='Fill Test Data'])[2]").click()
    page.wait_for_timeout(2000)
    page.locator("(//button[normalize-space()='Next'])[2]").click()
    page.wait_for_selector("//input[@name='fundingAmount']", state='visible', timeout=20000)

    def get_field_state(name):
        return page.evaluate("name => { const input = document.querySelector(`input[name='${name}']`); if (!input) return null; const root = input.closest('div.MuiFormControl-root'); return {name: name, value: input.value, ariaInvalid: input.getAttribute('aria-invalid'), className: input.className, rootClass: root ? root.className : null, errors: root ? Array.from(root.querySelectorAll('p, span, div')).map(el => ({tag: el.tagName, className: el.className, text: el.textContent.trim()})) : []}; }", name)

    def trigger_change(name, value=None):
        if value is None:
            page.locator(f"input[name='{name}']").click()
            page.locator(f"input[name='{name}']").press('Control+a')
            page.locator(f"input[name='{name}']").press('Delete')
            page.evaluate("name => { const input = document.querySelector(`input[name='${name}']`); if (!input) return; input.dispatchEvent(new Event('input', {bubbles:true})); input.dispatchEvent(new Event('change', {bubbles:true})); input.dispatchEvent(new Event('blur', {bubbles:true})); }", name)
        else:
            page.locator(f"input[name='{name}']").click()
            page.locator(f"input[name='{name}']").press('Control+a')
            page.locator(f"input[name='{name}']").press('Delete')
            page.evaluate("(name,val) => { const input = document.querySelector(`input[name='${name}']`); if (!input) return; input.value = val; input.dispatchEvent(new Event('input', {bubbles:true})); input.dispatchEvent(new Event('change', {bubbles:true})); input.dispatchEvent(new Event('blur', {bubbles:true})); }", name, value)
        page.wait_for_timeout(1500)

    print('factorRate before', get_field_state('factorRate'))
    trigger_change('factorRate')
    print('factorRate after clear', get_field_state('factorRate'))
    print('factorRate messages', page.evaluate("() => Array.from(document.querySelectorAll('*')).filter(el => el.textContent && el.textContent.toLowerCase().includes('factor rate')).map(el => ({tag: el.tagName, className: el.className, text: el.textContent.trim()}))"))
    print('aria invalid count', page.locator("input[aria-invalid='true']").count())

    print('fundingAmount before', get_field_state('fundingAmount'))
    trigger_change('fundingAmount', '0')
    print('fundingAmount after set0', get_field_state('fundingAmount'))
    print('fundingAmount messages', page.evaluate("() => Array.from(document.querySelectorAll('*')).filter(el => el.textContent && el.textContent.toLowerCase().includes('greater than zero')).map(el => ({tag: el.tagName, className: el.className, text: el.textContent.trim()}))"))
    print('aria invalid count', page.locator("input[aria-invalid='true']").count())
    browser.close()
