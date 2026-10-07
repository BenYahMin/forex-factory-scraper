import os
import json
import pandas as pd
from datetime import datetime

class DataStorage:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)

    def save_to_json(self, events, filename="forex_calendar.json"):
        """Saves events list to a JSON file."""
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(events, f, indent=4, ensure_ascii=False)
        print(f"Successfully saved {len(events)} events to JSON: {filepath}")

    def save_to_csv(self, events, filename="forex_calendar.csv"):
        """Saves events list to a CSV file using pandas."""
        if not events:
            print("No events to save to CSV.")
            return

        filepath = os.path.join(self.data_dir, filename)
        df = pd.DataFrame(events)
        df.to_csv(filepath, index=False, encoding="utf-8")
        print(f"Successfully saved {len(events)} events to CSV: {filepath}")

    def append_to_historical(self, events, filename="historical_calendar.csv"):
        """
        Appends new events to a historical dataset while removing duplicates 
        based on date, time, currency, and event name.
        """
        if not events:
            return

        filepath = os.path.join(self.data_dir, filename)
        new_df = pd.DataFrame(events)

        if os.path.exists(filepath):
            existing_df = pd.read_csv(filepath)
            # Combine and drop duplicates
            combined_df = pd.concat([existing_df, new_df]).drop_duplicates(
                subset=["date", "time", "currency", "event"], keep="last"
            )
            combined_df.to_csv(filepath, index=False, encoding="utf-8")
            print(f"Updated historical dataset. Total unique records: {len(combined_df)}")
        else:
            new_df.to_csv(filepath, index=False, encoding="utf-8")
            print(f"Created new historical dataset with {len(events)} records.")