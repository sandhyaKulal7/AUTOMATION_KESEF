import os
import json
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

    def json_print(label, value):
        print(f'--- {label} ---')
        print(json.dumps(value, indent=2)[:20000])

    def inspect_input(name):
        return page.evaluate(
            '''name => {
                const input = document.querySelector(`input[name='${name}']`);
                if (!input) return null;
                const root = input.closest('div.MuiFormControl-root');
                return {
                    name,
                    value: input.value,
                    ariaInvalid: input.getAttribute('aria-invalid'),
                    ariaDescribedBy: input.getAttribute('aria-describedby'),
                    className: input.className,
                    rootClass: root ? root.className : null,
                    rootOuter: root ? root.outerHTML.slice(0,1000) : null,
                    helperText: root ? Array.from(root.querySelectorAll('p, span, div')).filter(el => el.textContent.trim()).map(el => ({ tag: el.tagName, className: el.className, text: el.textContent.trim().slice(0,200), outerHTML: el.outerHTML.slice(0,400) })) : []
                };
            }''',
            name,
        )

    def find_texts(substr):
        return page.evaluate(
            '''substr => Array.from(document.querySelectorAll('*')).filter(el => el.textContent && el.textContent.toLowerCase().includes(substr.toLowerCase())).slice(0,40).map(el => ({ tag: el.tagName, className: el.className, text: el.textContent.trim(), outerHTML: el.outerHTML.slice(0,300) }))''',
            substr,
        )

    def find_errors():
        return page.evaluate(
            '''() => Array.from(document.querySelectorAll('*')).filter(el => el.className && el.className.toLowerCase().includes('error')).map(el => ({ tag: el.tagName, className: el.className, text: el.textContent.trim(), outerHTML: el.outerHTML.slice(0,300) }))''',
        )

    print('buttons:', page.evaluate("() => Array.from(document.querySelectorAll('button')).map(b => b.textContent.trim()).filter(Boolean)"))
    json_print('factorRate initial', inspect_input('factorRate'))
    json_print('fundingAmount initial', inspect_input('fundingAmount'))
    page.locator("input[name='factorRate']").click()
    page.locator("input[name='factorRate']").press('Control+a')
    page.locator("input[name='factorRate']").press('Delete')
    page.locator("input[name='factorRate']").press('Tab')
    page.wait_for_timeout(2500)
    json_print('factorRate after clear blur', inspect_input('factorRate'))
    json_print('factorRate find errors', find_errors())
    json_print('factorRate text matches required', find_texts('required'))
    page.locator("input[name='fundingAmount']").click()
    page.locator("input[name='fundingAmount']").press('Control+a')
    page.locator("input[name='fundingAmount']").press('Delete')
    page.keyboard.type('0')
    page.locator("input[name='fundingAmount']").press('Tab')
    page.wait_for_timeout(2500)
    json_print('fundingAmount after set 0 blur', inspect_input('fundingAmount'))
    json_print('fundingAmount find errors', find_errors())
    json_print('fundingAmount text matches greater than zero', find_texts('greater than zero'))
    json_print('after submit disabled state', page.evaluate("() => ({ submitDisabled: Array.from(document.querySelectorAll('button')).filter(b => b.textContent.trim()==='Submit').map(b => b.disabled) })"))
    page.locator("button:has-text('Submit')").click()
    page.wait_for_timeout(2500)
    json_print('after submit snackbars', page.evaluate("() => Array.from(document.querySelectorAll('[role=alert]')).map(el => ({ tag: el.tagName, className: el.className, text: el.textContent.trim(), outerHTML: el.outerHTML.slice(0,400) }))"))
    json_print('after submit text matches greater than zero', find_texts('greater than zero'))
    json_print('after submit text matches Factor Rate is required', find_texts('Factor Rate is required'))
    browser.close()
