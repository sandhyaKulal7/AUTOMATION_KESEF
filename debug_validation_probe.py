import os
from playwright.sync_api import sync_playwright

env = {}
with open('.env','r',encoding='utf-8') as f:
    for line in f:
        line=line.strip()
        if '=' in line and not line.startswith('#'):
            k,v=line.split('=',1); env[k]=v
BASE_URL = env.get('BASE_URL','https://kesef.qa.codezyng.com/')
EMAIL = env['TEST_EMAIL']
PASSWORD = env['TEST_PASSWORD']

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(base_url=BASE_URL, viewport={'width':1920,'height':1080})
    page = ctx.new_page()
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

    def inspect_field(name):
        return page.evaluate(
            "name => { const input = document.querySelector(`input[name='${name}']`); if(!input) return null; const root = input.closest('div.MuiFormControl-root'); return {
                name: name,
                value: input.value,
                type: input.type,
                ariaInvalid: input.getAttribute('aria-invalid'),
                ariaDescribedBy: input.getAttribute('aria-describedby'),
                className: input.className,
                rootClassName: root ? root.className : null,
                rootOuter: root ? root.outerHTML.slice(0,1000) : null,
                helperText: root ? Array.from(root.querySelectorAll('p, span, div')).filter(el => el.textContent.trim()).map(el => ({tag: el.tagName, className: el.className, text: el.textContent.trim().slice(0,200), outerHTML: el.outerHTML.slice(0,400)})) : []
            }; }",
            name
        )

    def find_error_elements():
        return page.evaluate(
            "() => Array.from(document.querySelectorAll('*')).filter(el => el.textContent && el.textContent.trim() && (el.textContent.toLowerCase().includes('factor rate') || el.textContent.toLowerCase().includes('greater than zero') || el.className.toLowerCase().includes('error') || el.getAttribute('role')==='alert' || el.id.toLowerCase().includes('error'))).map(el => ({tag: el.tagName, className: el.className, text: el.textContent.trim().slice(0,200), outerHTML: el.outerHTML.slice(0,400)}))"
        )

    print('factorRate pre', inspect_field('factorRate'))
    print('fundingAmount pre', inspect_field('fundingAmount'))

    page.locator("input[name='factorRate']").click()
    page.locator("input[name='factorRate']").press('Control+a')
    page.locator("input[name='factorRate']").press('Delete')
    page.locator("input[name='factorRate']").press('Tab')
    page.wait_for_timeout(2500)
    print('factorRate post blur', inspect_field('factorRate'))
    print('factorRate error candidates', find_error_elements())

    page.locator("input[name='fundingAmount']").click()
    page.locator("input[name='fundingAmount']").press('Control+a')
    page.locator("input[name='fundingAmount']").press('Delete')
    page.keyboard.type('0')
    page.locator("input[name='fundingAmount']").press('Tab')
    page.wait_for_timeout(2500)
    print('fundingAmount post blur', inspect_field('fundingAmount'))
    print('fundingAmount error candidates', find_error_elements())

    page.locator("button:has-text('Next')").last.click()
    page.wait_for_timeout(2500)
    print('after clicking Next step3 errors', find_error_elements())
    browser.close()
