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

def prompt_for_assertions(repository: ObjectRepository):
    """
    Prompts the user for assertions for each object in the repository.
    """
    print("\\n--- Add Assertions ---")
    print("For each object, you will be asked if you want to add a visibility assertion.")
    print("In a real environment, you would be prompted for input (y/n).")
    print("For this demonstration, we will automatically add a visibility assertion to each object.")

    for key, obj in repository.objects.items():
        print(f"Object: {obj['tag']}(name='{obj['name']}', text='{obj['text']}')")
        obj['assertions']['visible'] = True

    print("\\n--- Assertions Complete ---")
    return repository

async def main(seed_url: str, max_depth: int):
    repository = ObjectRepository()
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        crawler = Crawler(seed_url, max_depth)
        async for crawled_page in crawler.crawl(page):
            print(f"Enumerating objects on: {crawled_page.url}")
            objects = await enumerate_objects(crawled_page)
            for obj in objects:
                repository.add_object(obj, crawled_page.url)

        await browser.close()

    repository = prompt_for_assertions(repository)
    repository.save()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Web Automation Framework")
    parser.add_argument("url", help="The seed URL to start crawling.")
    parser.add_argument("--depth", type=int, default=2, help="The maximum depth to crawl.")
    args = parser.parse_args()

    asyncio.run(main(args.url, args.depth))
