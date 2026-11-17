import asyncio
from playwright.async_api import async_playwright

viewports = [
    ("Mobile Small", 360, 740),
    ("Mobile Standard", 390, 844),
    ("Mobile Large", 414, 896),
    ("Tablet Portrait", 768, 1024),
    ("Tablet Landscape", 1024, 768),
    ("Desktop", 1280, 800),
]

async def check_url(page, url, name, w, h):
    await page.set_viewport_size({"width": w, "height": h})
    await page.goto(url, wait_until="domcontentloaded")
    await asyncio.sleep(1.5)
    
    # Check for horizontal scroll overflow
    scroll_w, client_w = await page.evaluate(
        "() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]"
    )
    has_overflow = scroll_w > client_w
    status = "OVERFLOW!" if has_overflow else "OK"
    print(f"[{name} {w}x{h}] {url} -> scrollWidth: {scroll_w}, clientWidth: {client_w} => {status}")
    return has_overflow

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("=== AUDITING WEB TERMINAL DASHBOARD (http://127.0.0.1:8000/dashboard/) ===")
        for name, w, h in viewports:
            await check_url(page, "http://127.0.0.1:8000/dashboard/", name, w, h)
            
        print("\n=== AUDITING REACT + VITE FRONTEND (http://127.0.0.1:3000/) ===")
        for name, w, h in viewports:
            await check_url(page, "http://127.0.0.1:3000/", name, w, h)
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
