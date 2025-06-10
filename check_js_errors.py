import asyncio
from playwright.async_api import async_playwright

async def check_js_errors(file_path):
    """
    Loads a local HTML file in a headless browser and checks for console errors.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        console_errors = []

        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)

        await page.goto(f"file://{file_path}")

        # Give some time for scripts to execute and potential errors to be logged
        await asyncio.sleep(2)

        await browser.close()

        return console_errors

if __name__ == "__main__":
    html_file_path = "/app/index.html"  # Assuming index.html is in the /app directory
    print(f"Checking {html_file_path} for JavaScript console errors...")

    errors = asyncio.run(check_js_errors(html_file_path))

    if errors:
        print("JavaScript Console Errors Found:")
        for error in errors:
            print(f"- {error}")
    else:
        print("No JavaScript console errors found.")
