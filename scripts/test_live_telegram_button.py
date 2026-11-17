import asyncio
from playwright.async_api import async_playwright

async def test_live_telegram_login():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        print('Opening live website: https://taikry-ai-trading.onrender.com/')
        await page.goto('https://taikry-ai-trading.onrender.com/', wait_until='domcontentloaded')
        await asyncio.sleep(2)

        # Click Sign In button in header
        sign_in_btn = page.locator("header button:has-text('Sign In'), header button:has-text('ចូលគណនី')").first
        if await sign_in_btn.count() > 0:
            print('Clicking header Sign In button...')
            await sign_in_btn.click()
            await asyncio.sleep(1)

        modal = page.locator('text=ZYROX AI AUTHENTICATION')
        print('Auth modal displayed:', await modal.count() > 0)

        tg_btn = page.locator("button:has-text('Continue with Telegram'), button:has-text('បន្តជាមួយ Telegram')").first
        print('Clicking Telegram Login button...')

        try:
            async with page.expect_navigation(timeout=10000):
                await tg_btn.click()
            print('Navigated to URL:', page.url)
        except Exception as e:
            print('Current URL after click:', page.url)

        error_alert = page.locator('.bg-red-500\\/10')
        if await error_alert.count() > 0:
            print('Alert appeared:', await error_alert.inner_text())
        else:
            print('SUCCESS: No error alert! Directed to Telegram OAuth:', 'oauth.telegram.org' in page.url)

        await browser.close()

if __name__ == '__main__':
    asyncio.run(test_live_telegram_login())
