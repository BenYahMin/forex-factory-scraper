from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def parse_forex_calendar(html_content):
    """
    Parses the Forex Factory calendar HTML and extracts structured economic event data.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 
    table = soup.find('div', class_='calendar__table')
    if not table:
        print("Error: Could not locate 'calendar__table' in HTML. The DOM structure might have changed or page is a challenge screen.")
        return []

    rows = table.find_all('tr', class_='calendar__row')
    events = []
    
    current_date = ""
    current_time = ""

    for row in rows:
        # 1. Extract Date
        date_cell = row.find('td', class_='calendar__date')
        if date_cell and date_cell.text.strip():
            date_text = date_cell.text.strip()
            # Forex Factory usually shows dates like "Mon Jan 1" or similar
            current_date = date_text

        # 2. Extract Time
        time_cell = row.find('td', class_='calendar__time')
        if time_cell and time_cell.text.strip():
            time_text = time_cell.text.strip()
            if time_text.lower() not in ["all day", "tentative"]:
                current_time = time_text

        # 3. Extract Currency
        currency_cell = row.find('td', class_='calendar__currency')
        currency = currency_cell.text.strip() if currency_cell else ""
        
        if not currency:
            continue # Skip non-event header rows

        # 4. Extract Impact Level (High, Medium, Low, None)
        impact_cell = row.find('td', class_='calendar__impact')
        impact_span = impact_cell.find('span') if impact_cell else None
        impact = "None"
        if impact_span and 'class' in impact_span.attrs:
            # Classes usually contain 'icon--high', 'icon--medium', 'icon--low', 'icon--holiday'
            classes = " ".join(impact_span['class'])
            if 'high' in classes:
                impact = 'High'
            elif 'medium' in classes:
                impact = 'Medium'
            elif 'low' in classes:
                impact = 'Low'
            elif 'holiday' in classes:
                impact = 'Holiday'

        # 5. Extract Event Title
        event_cell = row.find('td', class_='calendar__event')
        event_title = event_cell.text.strip() if event_cell else ""

        # 6. Extract Actual, Forecast, and Previous Values
        actual_cell = row.find('td', class_='calendar__actual')
        forecast_cell = row.find('td', class_='calendar__forecast')
        previous_cell = row.find('td', class_='calendar__previous')

        actual = actual_cell.text.strip() if actual_cell else ""
        forecast = forecast_cell.text.strip() if forecast_cell else ""
        previous = previous_cell.text.strip() if previous_cell else ""

        # Append structured dictionary
        events.append({
            "date": current_date,
            "time": current_time,
            "currency": currency,
            "impact": impact,
            "event": event_title,
            "actual": actual,
            "forecast": forecast,
            "previous": previous
        })

    return events

if __name__ == "__main__":
    from scraper import fetch_calendar_html
    
    # Test parser with our fetcher module
    html = fetch_calendar_html()
    parsed_events = parse_forex_calendar(html)
    
    print(f"Successfully extracted {len(parsed_events)} events!")
    if parsed_events:
        print("Sample event:", parsed_events[0])