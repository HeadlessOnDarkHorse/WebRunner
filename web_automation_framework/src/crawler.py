import asyncio
from playwright.async_api import Page
from typing import Set, List, Dict, Tuple, AsyncGenerator
from urllib.parse import urljoin, urlparse
from aoda.scanner import run_aoda_scan

class Crawler:
    def __init__(self, seed_url: str, max_depth: int = 2, username: str = None, password: str = None, aoda_scan: bool = False):
        self.seed_url = seed_url
        self.domain = urlparse(seed_url).netloc
        self.urls_to_visit: List[Tuple[str, int]] = [(seed_url, 0)]
        self.visited_urls: Set[str] = set()
        self.max_depth = max_depth
        self.username = username
        self.password = password
        self.aoda_scan = aoda_scan
        self.aoda_results = []
        self.interacted_elements = {}

    async def _get_element_identifier(self, element):
        """
        Creates a unique identifier for a Playwright element.
        """
        tag = await element.evaluate('e => e.tagName')
        text = await element.text_content()
        return f"{tag.lower()}:{text.strip()}"

    async def _handle_login(self, page: Page):
        """
        Handles the login process for Azure Entra ID.
        """
        print("Login page detected. Handling login...")
        try:
            # Fill in the username
            await page.fill('input[name="loginfmt"]', self.username)
            await page.click('input[type="submit"]')

            # Wait for the password field to be visible
            await page.wait_for_selector('input[name="passwd"]')

            # Fill in the password
            await page.fill('input[name="passwd"]', self.password)
            await page.click('input[type="submit"]')

            # Wait for navigation after login
            await page.wait_for_navigation()
            print("Login successful.")

        except Exception as e:
            print(f"Failed to login: {e}")

    async def _scan_and_discover(self, page: Page, depth: int):
        """
        Helper method to run scans and discover new interactions.
        """
        if self.aoda_scan:
            print(f"  - Running AODA scan...")
            results = await run_aoda_scan(page)
            if results and results.get("violations"):
                self.aoda_results.append({"url": page.url, "results": results})

        yield page

        if depth < self.max_depth:
            print(f"  - Discovering interactions...")
            new_urls, new_page_states = await self.discover_and_interact(page)
            for new_url in new_urls:
                if new_url not in self.visited_urls:
                    self.urls_to_visit.append((new_url, depth + 1))

            for new_page_state in new_page_states:
                print(f"  - New page state detected on: {new_page_state.url}")
                async for p in self._scan_and_discover(new_page_state, depth):
                    yield p

    async def crawl(self, page: Page) -> AsyncGenerator[Page, None]:
        while self.urls_to_visit:
            url, depth = self.urls_to_visit.pop(0)

            if url in self.visited_urls or depth >= self.max_depth:
                continue

            self.visited_urls.add(url)
            print(f"Crawling: {url} (Depth: {depth})")

            try:
                await page.goto(url)

                if "login.microsoftonline.com" in page.url:
                    await self._handle_login(page)

                async for p in self._scan_and_discover(page, depth):
                    yield p

            except Exception as e:
                print(f"  - Failed to process page {url}: {e}")

    async def discover_and_interact(self, page: Page) -> Tuple[List[str], List[Page]]:
        discovered_urls = []
        new_page_states = []

        clickable_elements = await page.query_selector_all(
            "a[href], button, [role='button'], [role='link'], [role='tab']"
        )

        page_url = page.url
        if page_url not in self.interacted_elements:
            self.interacted_elements[page_url] = set()

        for element in clickable_elements:
            element_id = await self._get_element_identifier(element)
            if element_id in self.interacted_elements[page_url]:
                continue

            current_url = page.url
            try:
                await element.click()
                self.interacted_elements[page_url].add(element_id)

                if page.url != current_url:
                    if urlparse(page.url).netloc == self.domain:
                        discovered_urls.append(page.url)
                else:
                    new_page_states.append(page)

            except Exception as e:
                print(f"    - Failed to click element: {element_id}. Reason: {e}")

        return discovered_urls, new_page_states
