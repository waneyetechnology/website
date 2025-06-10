import asyncio
from playwright.async_api import async_playwright
import os

async def capture_screenshot(file_path, screenshot_path):
    """
    Loads a local HTML file in a headless browser and captures a screenshot.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Ensure the file path is absolute
        absolute_file_path = os.path.abspath(file_path)

        await page.goto(f"file://{absolute_file_path}")

        # Wait for a bit to ensure rendering is complete if needed,
        # though for a simple rectangle, it might not be strictly necessary.
        await page.wait_for_timeout(1000)

        await page.screenshot(path=screenshot_path)
        await browser.close()
        print(f"Screenshot saved to {screenshot_path}")

if __name__ == "__main__":
    html_file = "index.html"
    screenshot_file = "screenshot.png"

    # Make sure paths are relative to the /app directory where the script will run
    html_file_path_in_app = os.path.join("/app", html_file)
    screenshot_path_in_app = os.path.join("/app", screenshot_file)

    print(f"Capturing screenshot of {html_file_path_in_app}...")
    asyncio.run(capture_screenshot(html_file_path_in_app, screenshot_path_in_app))
