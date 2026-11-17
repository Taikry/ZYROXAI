import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from playwright.async_api import async_playwright

ARTIFACT_DIR = r"C:\Users\Heng Taikry\.gemini\antigravity\brain\0027cbf4-2408-4289-a06e-a2417b62a4fc"

async def test_url(url: str, label: str, cookies=None):
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="chrome", headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        if cookies:
            await context.add_cookies(cookies)
        page = await context.new_page()

        console_logs = []
        page_errors = []

        failed_requests = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
        page.on("pageerror", lambda exc: page_errors.append(str(exc)))
        page.on("requestfailed", lambda req: failed_requests.append(f"FAILED: {req.method} {req.url} - {req.failure}"))
        page.on("response", lambda res: failed_requests.append(f"HTTP {res.status}: {res.request.method} {res.url}") if res.status >= 400 else None)

        print(f"\n--- Testing {label}: {url} ---")
        try:
            resp = await page.goto(url, wait_until="load", timeout=15000)
            print(f"Status: {resp.status if resp else 'No response'}")
        except Exception as e:
            print(f"Navigation error: {e}")

        await page.wait_for_timeout(3500)

        # Check if loader element is present / visible
        loader = await page.query_selector("#zyrox-startup-loader")
        if loader:
            is_visible = await loader.is_visible()
            loader_class = await loader.get_attribute("class")
            loader_style = await loader.get_attribute("style")
            print(f"Loader exists! Visible: {is_visible}, Class: '{loader_class}', Style: '{loader_style}'")
        else:
            print("Loader element not found in DOM.")

        # Check address bar
        print(f"Current page URL: {page.url}")

        screenshot_path = os.path.join(ARTIFACT_DIR, f"{label}_screenshot.png")
        await page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")

        print(f"Failed requests ({len(failed_requests)}):")
        for fr in failed_requests:
            print(f"  {fr}")

        print(f"Page errors ({len(page_errors)}):")
        for err in page_errors:
            print(f"  [ERROR] {err}")

        print(f"Console logs ({len(console_logs)}):")
        for log in console_logs[:20]:
            print(f"  {log}")

        await browser.close()

async def main():
    # 1. First test local server with an active test session
    from taikry.database.session import SessionLocal
    from taikry.database.models import User, UserSession
    from taikry.saas.security import hash_token
    import secrets
    import datetime

    db = SessionLocal()
    token_raw = secrets.token_urlsafe(32)
    user = db.query(User).first()
    if user:
        st = UserSession(
            user_id=user.id,
            token_hash=hash_token(token_raw),
            expires_at=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7),
            ip_address="127.0.0.1",
            user_agent="Playwright"
        )
        db.add(st)
        db.commit()
    db.close()

    local_cookie = {
        "name": "zyrox_session",
        "value": token_raw,
        "domain": "127.0.0.1",
        "path": "/"
    }

    await test_url(
        "http://127.0.0.1:8000/dashboard/?auth_success=telegram&new_user=1",
        "local_dashboard_auth_test",
        cookies=[local_cookie]
    )

if __name__ == "__main__":
    asyncio.run(main())
