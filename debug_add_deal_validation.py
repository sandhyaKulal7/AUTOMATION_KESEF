import os
from playwright.sync_api import sync_playwright

# Load env variables from .env
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
    page.wait_for_selector("//input[@name='firstName']", state='visible', timeout=20000)
    page.locator("(//button[normalize-space()='Fill Test Data'])[1]").click()
    page.wait_for_timeout(2000)
    page.locator("(//button[normalize-space()='Next'])[1]").click()
    page.wait_for_selector("//div[@id='mui-component-select-brokerageId']", state='visible', timeout=20000)
    page.locator("(//button[normalize-space()='Fill Test Data'])[2]").click()
    page.wait_for_timeout(2000)
    page.locator("(//button[normalize-space()='Next'])[2]").click()
    page.wait_for_selector("//input[@name='fundingAmount']", state='visible', timeout=20000)

    def describe_selector(sel):
        return page.evaluate("sel => { const el = document.querySelector(sel); if (!el) return null; return { tag: el.tagName, text: el.textContent.trim(), className: el.className, outerHTML: el.outerHTML.slice(0,600) }; }", sel)

    def find_elements_with_text(txt):
        return page.evaluate("txt => Array.from(document.querySelectorAll('*')).filter(el => el.textContent && el.textContent.toLowerCase().includes(txt.toLowerCase())).slice(0,80).map(el => ({ tag: el.tagName, className: el.className, text: el.textContent.trim(), outerHTML: el.outerHTML.slice(0,400) })); ", txt)

    def find_relative_errors(name):
        return page.evaluate("name => { const input = document.querySelector(`input[name='${name}']`); if (!input) return []; const root = input.closest('div.MuiFormControl-root'); if (!root) return []; return Array.from(root.querySelectorAll('p, span, div')).map(el => ({ tag: el.tagName, className: el.className, text: el.textContent.trim(), outerHTML: el.outerHTML.slice(0,400) })); }", name)

    print('factorRate initial', describe_selector("input[name='factorRate']"))
    print('fundingAmount initial', describe_selector("input[name='fundingAmount']"))
    print('all buttons', page.evaluate("() => Array.from(document.querySelectorAll('button')).map(b => b.textContent.trim()).filter(Boolean)"))

    page.locator("input[name='factorRate']").click()
    page.locator("input[name='factorRate']").press('Control+a')
    page.locator("input[name='factorRate']").press('Delete')
    page.locator("input[name='factorRate']").press('Tab')
    page.wait_for_timeout(2000)
    print('factorRate after blur', describe_selector("input[name='factorRate']"))
    print('factorRate relative errors', find_relative_errors('factorRate'))
    print('text nodes containing "factor rate"', find_elements_with_text('Factor Rate'))
    print('text nodes containing "required"', find_elements_with_text('required'))
    print('role alerts', page.evaluate("() => Array.from(document.querySelectorAll('[role=alert]')).map(el => ({ tag: el.tagName, className: el.className, text: el.textContent.trim(), outerHTML: el.outerHTML.slice(0,400) }))"))

    page.locator("input[name='fundingAmount']").click()
    page.locator("input[name='fundingAmount']").press('Control+a')
    page.locator("input[name='fundingAmount']").press('Delete')
    page.keyboard.type('0')
    page.locator("input[name='fundingAmount']").press('Tab')
    page.wait_for_timeout(2000)
    print('fundingAmount after blur', describe_selector("input[name='fundingAmount']"))
    print('fundingAmount relative errors', find_relative_errors('fundingAmount'))
    print('text nodes containing "greater than zero"', find_elements_with_text('greater than zero'))
    print('all p with text', page.evaluate("() => Array.from(document.querySelectorAll('p')).filter(p => p.textContent.trim()).map(p => ({ text: p.textContent.trim(), className: p.className, outerHTML: p.outerHTML.slice(0,300) }))"))

    page.locator("button:text('Next')").last.click()
    page.wait_for_timeout(2000)
    print('after clicking Next on step 3, text nodes containing "factor rate"', find_elements_with_text('Factor Rate'))
    print('after clicking Next on step 3, text nodes containing "greater than zero"', find_elements_with_text('greater than zero'))
    browser.close()
