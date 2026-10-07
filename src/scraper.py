import os
import cloudscraper
from bs4 import BeautifulSoup

def fetch_calendar_html(local_fallback_path="data/raw_calendar.html", force_local=False):
    """
    Fetches the Forex Factory calendar page with automatic caching 
    and a local fallback mechanism if blocked or offline.
    """
    html_content = None
    
    # Attempt live fetch unless force_local is specified
    if not force_local:
        try:
            print("Attempting live fetch from Forex Factory...")
            scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'desktop': True
                }
            )
            url = "https://www.forexfactory.com/calendar?week=this"
            response = scraper.get(url, timeout=15)
            
            if response.status_code == 200:
                html_content = response.text
                
                # Cache the successful response locally for offline dev & fallbacks if they happen
                os.makedirs(os.path.dirname(local_fallback_path), exist_ok=True)
                with open(local_fallback_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                print("Live fetch successful! Saved fresh copy to local cache.")
            else:
                print(f"Live fetch returned status code {response.status_code}. Triggering local fallback...")
        except Exception as e:
            print(f"Live fetch failed due to error: {e}. Triggering local fallback...")

    # Fallback to local file if live fetch failed 
    if not html_content and os.path.exists(local_fallback_path):
        print(f"Loading HTML from local fallback file: {local_fallback_path}")
        with open(local_fallback_path, "r", encoding="utf-8") as f:
            html_content = f.read()
    elif not html_content:
        raise FileNotFoundError(
            f"Live fetch failed and no local fallback file found at '{local_fallback_path}'. "
            "To use manual mode, save a Forex Factory calendar HTML page to that path."
        )
        
    return html_content

if __name__ == "__main__":
    # Test the fetcher module
    html = fetch_calendar_html()
    soup = BeautifulSoup(html, 'html.parser')
    
    # Quick sanity check
    title = soup.title.string if soup.title else "No title found"
    print(f"Successfully loaded page. Page title: {title}")