import asyncio
import json
from playwright.async_api import Page

async def run_aoda_scan(page: Page):
    """
    Runs an Axe accessibility scan on the given Playwright page.

    Args:
        page (Page): The Playwright page object to scan.
    """
    try:
        # Inject the Axe script from a CDN
        await page.add_script_tag(url='https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.4.1/axe.min.js')

        # Run the scanner
        results = await page.evaluate('axe.run()')
        return results

    except Exception as e:
        print(f"Error running AODA scan on {page.url}: {e}")
        return None
