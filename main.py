from src.scraper import fetch_calendar_html
from src.parser import parse_forex_calendar
from src.storage import DataStorage

def main():
    print("--- Starting Forex Factory Scraper Pipeline ---")
    
    # Fetches HTML content from Forex Factory calendar
    html_content = fetch_calendar_html()
    
    # Parse calendar events
    events = parse_forex_calendar(html_content)
    
    if events:
        # Store data
        storage = DataStorage()
        storage.save_to_json(events)
        storage.save_to_csv(events)
        storage.append_to_historical(events)
        print("--- Pipeline Completed Successfully ---")
    else:
        # If no events are found, it will print a message
        print("--- Pipeline Completed: No events found ---")

if __name__ == "__main__":
    main()