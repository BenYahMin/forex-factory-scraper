import logging
import time
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class ForexFactoryFetcher:
    def __init__(self, max_retries: int = 3, backoff_factor: int = 2):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.base_url = "https://www.forexfactory.com/calendar"

    def fetch_calendar(self, date_str: str = None) -> str | None:
        url = f"{self.base_url}?day={date_str}" if date_str else self.base_url

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            for attempt in range(self.max_retries):
                try:
                    logger.info(f"Fetching data from {url} via Playwright (Attempt {attempt + 1}/{self.max_retries})")
                    page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    
                    # Wait for the calendar table element to be rendered
                    page.wait_for_selector("table.calendar__table", timeout=12000)
                    html_content = page.content()
                    
                    browser.close()
                    return html_content

                except Exception as e:
                    logger.error(f"Playwright fetch failed: {e}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.backoff_factor ** attempt)

            browser.close()
            return None