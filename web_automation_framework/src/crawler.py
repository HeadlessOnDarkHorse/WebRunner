import asyncio
from playwright.async_api import Page
from typing import Set, List, Dict, Tuple, AsyncGenerator
from urllib.parse import urljoin, urlparse

class Crawler:
    def __init__(self, seed_url: str, max_depth: int = 2):
        self.seed_url = seed_url
        self.domain = urlparse(seed_url).netloc
        self.urls_to_visit: List[Tuple[str, int]] = [(seed_url, 0)]
        self.visited_urls: Set[str] = set()
        self.max_depth = max_depth

    async def crawl(self, page: Page) -> AsyncGenerator[Page, None]:
        while self.urls_to_visit:
            url, depth = self.urls_to_visit.pop(0)

            if url in self.visited_urls or depth >= self.max_depth:
                continue

            print(f"Crawling: {url} at depth {depth}")
            try:
                await page.goto(url)
                self.visited_urls.add(url)
                yield page
            except Exception as e:
                print(f"Failed to crawl {url}: {e}")
                continue

            if depth < self.max_depth:
                new_urls = await self.discover_and_interact(page)
                for new_url in new_urls:
                    if new_url not in self.visited_urls:
                        self.urls_to_visit.append((new_url, depth + 1))

    async def discover_and_interact(self, page: Page, max_interactions: int = 10) -> List[str]:
        discovered_urls = []

        # Discover and process links
        links = await page.query_selector_all("a")
        for i, link in enumerate(links):
            if len(discovered_urls) >= max_interactions:
                break
            href = await link.get_attribute("href")
            if href:
                full_url = urljoin(page.url, href)
                if urlparse(full_url).netloc == self.domain:
                    discovered_urls.append(full_url)

        # Discover and process buttons
        buttons = await page.query_selector_all("button")
        for i, button in enumerate(buttons):
            if len(discovered_urls) >= max_interactions:
                break
            try:
                async with page.expect_navigation():
                    await button.click()
                new_url = page.url
                if urlparse(new_url).netloc == self.domain:
                    discovered_urls.append(new_url)
            except Exception as e:
                # This button click did not result in a navigation.
                pass

        return discovered_urls
