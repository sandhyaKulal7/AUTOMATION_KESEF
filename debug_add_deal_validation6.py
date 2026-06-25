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
    context = browser.new_context(base_url=BASE_URL, viewport={'width': 1920, 'height': 1080})
    page = context.new_page()
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

    def log(title, value):
        print(f"--- {title} ---")
        print(value)

    def text_matches(substr):
        return page.evaluate(
            "substr => Array.from(document.querySelectorAll('*')).filter(el => el.textContent && el.textContent.toLowerCase().includes(substr.toLowerCase())).map(el => ({tag: el.tagName, className: el.className, text: el.textContent.trim()})).slice(0,20))",
            substr,
        )

    def errors():
        return page.evaluate(
            "() => Array.from(document.querySelectorAll('p.MuiFormHelperText-root.Mui-error, span.MuiFormHelperText-root.Mui-error, div.MuiFormHelperText-root.Mui-error')).map(el => ({tag: el.tagName, className: el.className, text: el.textContent.trim()}))"
        )

    log('factorRate initial value', page.locator("input[name='factorRate']").input_value())
    log('fundingAmount initial value', page.locator("input[name='fundingAmount']").input_value())
    log('existing errors before clearing', errors())

    page.locator("input[name='factorRate']").click()
    page.locator("input[name='factorRate']").press('Control+a')
    page.locator("input[name='factorRate']").press('Delete')
    page.locator("input[name='factorRate']").press('Tab')
    page.wait_for_timeout(1500)
    log('factorRate value after clear', page.locator("input[name='factorRate']").input_value())
    log('errors after factorRate clear', errors())
    log('factorRate aria-invalid', page.locator("input[name='factorRate']").get_attribute('aria-invalid'))
    log('factorRate aria-describedby', page.locator("input[name='factorRate']").get_attribute('aria-describedby'))
    log('factorRate root html', page.evaluate("() => document.querySelector('input[name=\'factorRate\']')?.closest('div.MuiFormControl-root')?.outerHTML.slice(0,800) || 'missing'"))

    page.locator("input[name='fundingAmount']").click()
    page.locator("input[name='fundingAmount']").press('Control+a')
    page.locator("input[name='fundingAmount']").press('Delete')
    page.keyboard.type('0')
    page.locator("input[name='fundingAmount']").press('Tab')
    page.wait_for_timeout(1500)
    log('fundingAmount value after set 0', page.locator("input[name='fundingAmount']").input_value())
    log('errors after fundingAmount set 0', errors())
    log('fundingAmount aria-invalid', page.locator("input[name='fundingAmount']").get_attribute('aria-invalid'))
    log('fundingAmount aria-describedby', page.locator("input[name='fundingAmount']").get_attribute('aria-describedby'))
    log('fundingAmount root html', page.evaluate("() => document.querySelector('input[name=\'fundingAmount\']')?.closest('div.MuiFormControl-root')?.outerHTML.slice(0,800) || 'missing'"))

    page.locator("(//button[normalize-space()='Next'])[3]").click()
    page.wait_for_timeout(1500)
    log('after click next 3 errors', errors())
    log('all text greater than zero', text_matches('greater than zero'))
    log('all text factor rate is required', text_matches('factor rate is required'))

    browser.close()
