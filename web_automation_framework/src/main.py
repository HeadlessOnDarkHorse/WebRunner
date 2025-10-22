import asyncio
import argparse
import json
from playwright.async_api import async_playwright, Page
from typing import List, Dict
from crawler import Crawler
from object_repository import ObjectRepository

async def enumerate_objects(page: Page) -> List[Dict]:
    """
    Enumerates all interactable objects on the page.
    """
    interactable_elements = await page.query_selector_all(
        "a, button, input, select, textarea, [role='button'], [role='link']"
    )

    objects = []
    for element in interactable_elements:
        tag = await element.evaluate("el => el.tagName")
        name = await element.get_attribute("name")
        text = await element.text_content()
        role = await element.get_attribute("role")
        objects.append({"tag": tag, "name": name, "text": text, "role": role})

    return objects

def apply_assertions_from_config(repository: ObjectRepository, config_path: str = "assertion_config.json"):
    """
    Applies assertions to the repository based on a configuration file.
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        default_assertions = config.get("default_assertions", [])

        for key, obj in repository.objects.items():
            obj['assertions'] = default_assertions
    except FileNotFoundError:
        print(f"Warning: {config_path} not found. No assertions will be applied.")

    return repository

def save_sitemap(visited_urls: List[str], sitemap_path: str = "sitemap.json"):
    """
    Saves the list of visited URLs to a sitemap file.
    """
    with open(sitemap_path, "w") as f:
        json.dump(visited_urls, f, indent=4)
    print(f"Sitemap saved to: {sitemap_path}")

def display_crawl_summary(visited_urls: List[str], repository: ObjectRepository):
    """
    Displays a summary of the crawl.
    """
    print("\n--- Crawl Summary ---")
    print(f"Pages visited: {len(visited_urls)}")
    print("Pages:")
    for url in visited_urls:
        print(f"  - {url}")

    print(f"\nUnique objects found: {len(repository.objects)}")
    print("Objects:")
    for key, obj in repository.objects.items():
        print(f"  - {obj['tag']}(name='{obj['name']}', text='{obj['text']}')")
    print("--- End of Summary ---")

async def main(seed_url: str, max_depth: int):
    repository = ObjectRepository()
    visited_urls = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        crawler = Crawler(seed_url, max_depth)
        async for crawled_page in crawler.crawl(page):
            print(f"Enumerating objects on: {crawled_page.url}")
            objects = await enumerate_objects(crawled_page)
            for obj in objects:
                repository.add_object(obj, crawled_page.url)

        visited_urls = list(crawler.visited_urls)
        await browser.close()

    display_crawl_summary(visited_urls, repository)
    save_sitemap(visited_urls)
    repository = apply_assertions_from_config(repository)
    repository.save()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Web Automation Framework")
    parser.add_argument("url", help="The seed URL to start crawling.")
    parser.add_argument("--depth", type=int, default=1, help="The maximum depth to crawl.")
    args = parser.parse_args()

    asyncio.run(main(args.url, args.depth))
