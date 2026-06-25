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
    page.wait_for_selector("//input[@name='firstName']", state='visible', timeout=20000)
    page.locator("(//button[normalize-space()='Fill Test Data'])[1]").click()
    page.wait_for_timeout(2000)
    page.locator("(//button[normalize-space()='Next'])[1]").click()
    page.wait_for_selector("//div[@id='mui-component-select-brokerageId']", state='visible', timeout=20000)
    page.locator("(//button[normalize-space()='Fill Test Data'])[2]").click()
    page.wait_for_timeout(2000)
    page.locator("(//button[normalize-space()='Next'])[2]").click()
    page.wait_for_selector("//input[@name='fundingAmount']", state='visible', timeout=20000)

    def inspect(name):
        return page.evaluate(
            "name => {
                const input = document.querySelector(`input[name='${name}']`);
                if (!input) return null;
                const root = input.closest('div.MuiFormControl-root');
                const described = input.getAttribute('aria-describedby');
                const describedNodes = described ? described.split(' ').map(id => document.getElementById(id)).filter(Boolean).map(el => ({tag: el.tagName, className: el.className, text: el.textContent.trim(), outerHTML: el.outerHTML.slice(0,400)})) : [];
                const siblings = root ? Array.from(root.querySelectorAll('p, span, div, label')).map(el => ({tag: el.tagName, className: el.className, text: el.textContent.trim(), outerHTML: el.outerHTML.slice(0,400)})) : [];
                return {
                    name,
                    value: input.value,
                    type: input.type,
                    ariaInvalid: input.getAttribute('aria-invalid'),
                    ariaDescribedBy: described,
                    described: describedNodes,
                    inputClass: input.className,
                    rootClass: root ? root.className : None,
                    rootOuter: root ? root.outerHTML.slice(0,1000) : None,
                    siblings: siblings,
                };
            }",
            name,
        )

    def find_text(text):
        return page.evaluate(
            "text => Array.from(document.querySelectorAll('*')).filter(el => el.textContent && el.textContent.toLowerCase().includes(text.toLowerCase())).slice(0,60).map(el => ({tag: el.tagName, className: el.className, text: el.textContent.trim(), outerHTML: el.outerHTML.slice(0,400)}))",
            text,
        )

    def count_by_selector(selector):
        return page.locator(selector).count()

    print('factorRate pre', inspect('factorRate'))
    print('fundingAmount pre', inspect('fundingAmount'))

    page.locator("input[name='factorRate']").click()
    page.locator("input[name='factorRate']").press('Control+a')
    page.locator("input[name='factorRate']").press('Delete')
    page.locator("input[name='factorRate']").press('Tab')
    page.wait_for_timeout(2500)
    print('factorRate post blur', inspect('factorRate'))
    print('factorRate has error texts', find_text('Factor Rate is required'))
    print('factorRate has any error text', find_text('required'))
    print('aria-invalid true count', count_by_selector("input[aria-invalid='true']"))

    page.locator("input[name='fundingAmount']").click()
    page.locator("input[name='fundingAmount']").press('Control+a')
    page.locator("input[name='fundingAmount']").press('Delete')
    page.keyboard.type('0')
    page.locator("input[name='fundingAmount']").press('Tab')
    page.wait_for_timeout(2500)
    print('fundingAmount post blur', inspect('fundingAmount'))
    print('fundingAmount has error texts', find_text('Funding Amount must be greater than zero'))
    print('fundingAmount has any error text', find_text('greater than zero'))
    print('aria-invalid true count', count_by_selector("input[aria-invalid='true']"))

    page.locator("button:has-text('Next')").last.click()
    page.wait_for_timeout(2500)
    print('after click next on step3 factorRate text', find_text('Factor Rate is required'))
    print('after click next on step3 greater than zero text', find_text('greater than zero'))
    print('after click next on step3 aria-invalid true count', count_by_selector("input[aria-invalid='true']"))
    print('after click next on step3 all aria-invalid values', page.evaluate("() => Array.from(document.querySelectorAll('input[aria-invalid]')).map(i => ({name:i.name, aria:i.getAttribute('aria-invalid'), value:i.value}))"))
    browser.close()
