import asyncio
import os
from playwright.async_api import async_playwright

artifact_dir = r"C:\Users\Heng Taikry\.gemini\antigravity\brain\0027cbf4-2408-4289-a06e-a2417b62a4fc"

async def test_dashboard_mobile(page):
    print("\n--- Testing Web Terminal Dashboard on Mobile (390x844) ---")
    await page.set_viewport_size({"width": 390, "height": 844})
    await page.goto("http://127.0.0.1:8000/dashboard/", wait_until="domcontentloaded")
    await asyncio.sleep(2)

    # 1. Click "More" bottom nav button
    more_btn = page.locator("#mob-nav-more")
    await more_btn.click()
    await asyncio.sleep(0.5)

    # Check that sheet is visible
    sheet = page.locator("#mobile-more-sheet")
    is_visible = await sheet.is_visible()
    print(f"  Mobile More Sheet opened: {is_visible}")

    # Check button count inside sheet
    buttons = await sheet.locator(".mobile-more-btn").all()
    print(f"  Total buttons in Mobile More Sheet: {len(buttons)}")

    # Take screenshot of Mobile More Sheet
    more_shot = os.path.join(artifact_dir, "mobile_more_sheet_preview.png")
    await page.screenshot(path=more_shot)
    print(f"  Saved screenshot: {more_shot}")

    # 2. Test opening Trade Journal from mobile more sheet
    journal_btn = sheet.locator("button:has-text('Trade Journal & PnL')")
    await journal_btn.click()
    await asyncio.sleep(0.8)
    journal_modal = page.locator("#modal-trade-journal")
    j_visible = await journal_modal.is_visible()
    print(f"  Trade Journal Modal opened from mobile sheet: {j_visible}")
    if j_visible:
        # Close modal
        close_btn = journal_modal.locator(".modal-close-btn")
        if await close_btn.count() > 0:
            await close_btn.first.click()
        await asyncio.sleep(0.4)

    # 3. Test opening VIP Plans modal from mobile more sheet
    await more_btn.click()
    await asyncio.sleep(0.4)
    vip_btn = sheet.locator("button:has-text('VIP Plans & Quotas')")
    await vip_btn.click()
    await asyncio.sleep(0.8)
    vip_modal = page.locator("#plans-spec-modal")
    vip_visible = await vip_modal.is_visible()
    print(f"  VIP Plans Modal opened from mobile sheet: {vip_visible}")
    if vip_visible:
        close_btn = vip_modal.locator(".modal-close-btn")
        if await close_btn.count() > 0:
            await close_btn.first.click()
        await asyncio.sleep(0.4)

    # 4. Test opening Windows MT5 Bridge modal from mobile more sheet
    await more_btn.click()
    await asyncio.sleep(0.4)
    bridge_btn = sheet.locator("button:has-text('Windows MT5 Bridge')")
    await bridge_btn.click()
    await asyncio.sleep(0.8)
    bridge_modal = page.locator("#exness-mt5-bridge-modal")
    b_visible = await bridge_modal.is_visible()
    print(f"  Windows MT5 Bridge Modal opened from mobile sheet: {b_visible}")
    if b_visible:
        close_btn = bridge_modal.locator(".modal-close-btn")
        if await close_btn.count() > 0:
            await close_btn.first.click()
        await asyncio.sleep(0.4)

    # 5. Test opening V6 Concept Explorer from mobile sheet
    await more_btn.click()
    await asyncio.sleep(0.4)
    v6_btn = sheet.locator("button:has-text('V6 Concept Explorer')")
    await v6_btn.click()
    await asyncio.sleep(0.8)
    v6_modal = page.locator("#modal-v6-concept-explorer")
    v6_visible = await v6_modal.is_visible()
    print(f"  V6 Concept Explorer Modal opened from mobile sheet: {v6_visible}")
    if v6_visible:
        close_btn = v6_modal.locator(".modal-close-btn")
        if await close_btn.count() > 0:
            await close_btn.first.click()
        await asyncio.sleep(0.4)

    # 6. Test opening Signal Center overlay from mobile sheet
    await more_btn.click()
    await asyncio.sleep(0.4)
    sig_btn = sheet.locator("button:has-text('Signal Center')")
    await sig_btn.click()
    await asyncio.sleep(0.8)
    sig_overlay = page.locator("#tab-pane-signals")
    sig_visible = await sig_overlay.is_visible()
    print(f"  Signal Center Overlay opened from mobile sheet: {sig_visible}")
    if sig_visible:
        # Click back to terminal
        back_btn = sig_overlay.locator("button:has-text('Back to Terminal')")
        if await back_btn.count() > 0:
            await back_btn.first.click()
        await asyncio.sleep(0.4)

async def test_react_mobile(page):
    print("\n--- Testing React Frontend on Mobile (360x740) ---")
    await page.set_viewport_size({"width": 360, "height": 740})
    await page.goto("http://127.0.0.1:3000/", wait_until="domcontentloaded")
    await asyncio.sleep(2)

    # Open mobile hamburger menu
    menu_btn = page.locator("button[aria-label='Toggle navigation menu']")
    await menu_btn.click()
    await asyncio.sleep(0.5)

    # Verify all buttons in mobile drawer
    drawer_buttons = await page.locator("nav .pt-4 button, nav .pt-4 a").all_inner_texts()
    print(f"  React Mobile Drawer Actions: {drawer_buttons}")

    # Screenshot mobile drawer
    react_menu_shot = os.path.join(artifact_dir, "react_mobile_drawer_preview.png")
    await page.screenshot(path=react_menu_shot)
    print(f"  Saved screenshot: {react_menu_shot}")

    # Click "System AI Engine" inside mobile drawer
    sys_ai_btn = page.locator("nav .pt-4 button:has-text('System AI')")
    await sys_ai_btn.click()
    await asyncio.sleep(1)

    # Verify TerminalModal is open
    modal = page.locator("text=ZYROX SYSTEM AI")
    m_visible = await modal.count() > 0
    print(f"  TerminalModal opened: {m_visible}")
    
    # Check horizontal overflow
    scroll_w, client_w = await page.evaluate(
        "() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]"
    )
    print(f"  TerminalModal 360px viewport -> scrollWidth: {scroll_w}, clientWidth: {client_w} (Overflow: {scroll_w > client_w})")
    
    sys_shot = os.path.join(artifact_dir, "react_terminal_modal_mobile.png")
    await page.screenshot(path=sys_shot)
    print(f"  Saved screenshot: {sys_shot}")

    # Close modal
    close_btn = page.locator("button[aria-label='Close modal']")
    if await close_btn.count() > 0:
        await close_btn.first.click()
    await asyncio.sleep(0.5)

    # Open AuthModal via drawer
    await menu_btn.click()
    await asyncio.sleep(0.4)
    sign_in_btn = page.locator("nav .pt-4 button:has-text('Sign In')")
    await sign_in_btn.click()
    await asyncio.sleep(1)

    auth_modal = page.locator("text=ZYROX AI AUTHENTICATION")
    auth_visible = await auth_modal.count() > 0
    print(f"  AuthModal opened: {auth_visible}")

    auth_shot = os.path.join(artifact_dir, "react_auth_modal_mobile.png")
    await page.screenshot(path=auth_shot)
    print(f"  Saved screenshot: {auth_shot}")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await test_dashboard_mobile(page)
        await test_react_mobile(page)
        await browser.close()
        print("\nAll mobile & cross-device tests completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
