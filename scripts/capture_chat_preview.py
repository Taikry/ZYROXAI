import asyncio
import os
from playwright.async_api import async_playwright

ARTIFACT_DIR = r"C:\Users\Heng Taikry\.gemini\antigravity\brain\0027cbf4-2408-4289-a06e-a2417b62a4fc"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        url = "http://127.0.0.1:3000"
        print(f"Navigating to {url}...")
        try:
            await page.goto(url, wait_until="networkidle", timeout=15000)
        except Exception:
            # Fallback to direct dashboard URL
            url = "http://127.0.0.1:8000/dashboard/"
            print(f"Trying direct dashboard {url}...")
            await page.goto(url, wait_until="networkidle", timeout=15000)

        # Wait for chat input
        print("Waiting for chat input...")
        chat_input = page.locator("#ai-chat-input")
        await chat_input.wait_for(state="visible", timeout=10000)

        # Type 'HELLO'
        print("Typing 'HELLO'...")
        await chat_input.fill("HELLO")
        await page.wait_for_timeout(500)

        # Click send button
        print("Clicking Send...")
        send_btn = page.locator("#btn-chat-send")
        await send_btn.click()

        # Wait for conversational card response
        print("Waiting for conversational response card...")
        conv_card = page.locator(".chat-conversational-card")
        try:
            await conv_card.wait_for(state="visible", timeout=15000)
            print("Conversational card rendered successfully!")
        except Exception as e:
            print(f"Notice waiting for conv_card: {e}")

        await page.wait_for_timeout(2000)

        # Take screenshot of full dashboard
        full_path = os.path.join(ARTIFACT_DIR, "chat_hello_full_preview.png")
        await page.screenshot(path=full_path, full_page=False)
        print(f"Saved full preview to {full_path}")

        # Take screenshot of chat sidebar specifically
        sidebar = page.locator("#ai-sidebar-pane")
        if await sidebar.count() > 0:
            sidebar_path = os.path.join(ARTIFACT_DIR, "chat_conversational_sidebar.png")
            await sidebar.screenshot(path=sidebar_path)
            print(f"Saved sidebar preview to {sidebar_path}")

        await browser.close()
        print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
