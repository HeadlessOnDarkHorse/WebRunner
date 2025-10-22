import asyncio
import argparse
import json
from playwright.async_api import async_playwright, Page
from typing import List, Dict

def get_robust_selector(obj: Dict) -> str:
    """
    Generates a robust selector for an object.
    """
    selector = obj['tag']
    if obj.get('name'):
        selector += f"[name='{obj['name']}']"
    if obj.get('text'):
        # Sanitize text for CSS selector
        sanitized_text = obj['text'].replace("'", "\\'").replace('"', '\\"')
        selector += f":has-text(\"{sanitized_text}\")"
    return selector

class TestRunner:
    def __init__(self, repository_path: str = "object_repository.json", browser_type: str = "chromium"):
        self.repository_path = repository_path
        with open(self.repository_path, 'r') as f:
            self.objects = json.load(f)
        self.test_results = []
        self.browser_type = browser_type

    async def run_tests(self):
        async with async_playwright() as p:
            browser = None
            if self.browser_type == "chromium":
                browser = await p.chromium.launch()
            elif self.browser_type == "firefox":
                browser = await p.firefox.launch()
            elif self.browser_type == "webkit":
                browser = await p.webkit.launch()
            else:
                raise ValueError(f"Unsupported browser type: {self.browser_type}")

            page = await browser.new_page()

            try:
                for obj in self.objects:
                    for page_url in obj["pages"]:
                        await self.run_assertions_for_object(page, obj, page_url)
            except Exception as e:
                print(f"CRITICAL FAILURE: {e}")
            finally:
                await browser.close()

        return self.test_results

    async def run_assertions_for_object(self, page: Page, obj: Dict, page_url: str):
        await page.goto(page_url)

        selector = get_robust_selector(obj)

        for assertion in obj["assertions"]:
            element = await page.query_selector(selector)

            result = False
            reason = ""
            if assertion["property"] == "isVisible":
                if element is None:
                    result = False
                    reason = "Element not found"
                else:
                    result = await element.is_visible()
                    if not result:
                        reason = "Element is not visible"
            elif assertion["property"] == "isEnabled":
                if element is None:
                    result = False
                    reason = "Element not found"
                else:
                    result = await element.is_enabled()
                    if not result:
                        reason = "Element is not enabled"
            elif assertion["property"] == "hasText":
                if element is None:
                    result = False
                    reason = "Element not found"
                else:
                    actual_text = await element.text_content()
                    result = actual_text == assertion["expected"]
                    if not result:
                        reason = f"Expected text '{assertion['expected']}' but got '{actual_text}'"

            status = "passed" if result == assertion["expected"] else "failed"

            report_entry = {
                "object": obj,
                "page": page_url,
                "assertion": assertion,
                "status": status,
                "browser": self.browser_type
            }
            if status == "failed":
                report_entry["reason"] = reason

            self.test_results.append(report_entry)

            if status == "failed" and assertion["policy"] == "Critical":
                raise Exception(f"Critical assertion failed for object: {selector} on page {page_url}. Reason: {reason}")

    def save_report(self, report_path: str = "test_results.json"):
        with open(report_path, "w") as f:
            json.dump(self.test_results, f, indent=4)
        print(f"Test report saved to: {report_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Test Runner")
    parser.add_argument("--browser", type=str, default="chromium", help="Browser to use for testing (chromium, firefox, webkit)")
    args = parser.parse_args()

    async def main():
        runner = TestRunner(browser_type=args.browser)
        await runner.run_tests()
        runner.save_report()

    asyncio.run(main())
