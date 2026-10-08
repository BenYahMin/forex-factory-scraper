from pathlib import Path
from playwright.sync_api import sync_playwright

CACHE_PATH = Path("data/raw_calendar.html")
TARGET_URL = "https://www.forexfactory.com/calendar"

def fetch_calendar_html() -> str:
    """
    Fetches the Forex Factory calendar using a stealthy browser instance 
    to bypass Cloudflare checks.
    """
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        print("Launching browser for live fetch...")
        with sync_playwright() as p:
            # Launch with headless=False and hide automation flags
            browser = p.chromium.launch(
                headless=False,
                args=["--disable-blink-features=AutomationControlled"]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800}
            )
            page = context.new_page()
            
            print(f"Navigating to {TARGET_URL}...")
            page.goto(TARGET_URL, timeout=60000)
            
            print("Waiting for calendar DOM elements to render...")
            # Give it 30 seconds and watch the browser window that pops up
            page.wait_for_selector(".calendar__table", timeout=30000)
            
            html_content = page.content()
            browser.close()
            
            # Save fresh copy to local cache
            CACHE_PATH.write_text(html_content, encoding="utf-8")
            print("Live fetch successful! Saved fresh copy to local cache.")
            return html_content
            
    except Exception as e:
        print(f"Live fetch failed or blocked: {e}")
        if CACHE_PATH.exists():
            print(f"Falling back to local cache: {CACHE_PATH}")
            try:
                return CACHE_PATH.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                return CACHE_PATH.read_text(encoding="latin-1", errors="ignore")
        else:
            raise RuntimeError("Live fetch failed and no local cache found at data/raw_calendar.html")