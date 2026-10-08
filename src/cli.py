import argparse
import logging
from datetime import datetime, timedelta
import pandas as pd
from fetcher import ForexFactoryFetcher
from parser import ForexFactoryParser
from cleaner import ForexFactoryCleaner

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def generate_ff_date_str(dt: datetime) -> str:
    month = dt.strftime("%b").lower()
    return f"{month}{dt.day}.{dt.year}"

def scrape_range(start_date: str, end_date: str) -> pd.DataFrame:
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    fetcher = ForexFactoryFetcher()
    parser = ForexFactoryParser()
    cleaner = ForexFactoryCleaner()

    all_cleaned_events = []
    current_dt = start_dt

    while current_dt <= end_dt:
        ff_date = generate_ff_date_str(current_dt)
        logger.info(f"Processing date: {current_dt.strftime('%Y-%m-%d')} ({ff_date})")

        html_content = fetcher.fetch_calendar(date_str=ff_date)
        if html_content:
            raw_events = parser.parse_html(html_content)
            for raw_ev in raw_events:
                cleaned_ev = cleaner.clean_event(raw_ev, year=current_dt.year)
                all_cleaned_events.append(cleaned_ev)
        else:
            logger.warning(f"Skipping {ff_date} due to fetch failure.")

        current_dt += timedelta(days=1)

    return pd.DataFrame(all_cleaned_events)

def main():
    parser = argparse.ArgumentParser(description="Forex Factory Calendar Scraper & Exporter CLI")
    parser.add_argument("-s", "--start-date", type=str, required=True, help="Start date in YYYY-MM-DD format")
    parser.add_argument("-e", "--end-date", type=str, help="End date in YYYY-MM-DD format")
    parser.add_argument("-o", "--output", type=str, default="data/forex_factory_events.csv", help="Output file path")
    parser.add_argument("-f", "--format", choices=["csv", "parquet", "json"], default="csv", help="Export format")
    parser.add_argument("--min-impact", choices=["High", "Medium", "Low"], help="Filter by minimum impact level")

    args = parser.parse_args()
    end_date = args.end_date if args.end_date else args.start_date

    logger.info(f"Starting Forex Factory scrape pipeline from {args.start_date} to {end_date}...")
    df = scrape_range(args.start_date, end_date)

    if df.empty:
        logger.warning("No records collected.")
        return

    if args.min_impact:
        impact_thresholds = {"High": 3, "Medium": 2, "Low": 1}
        min_score = impact_thresholds[args.min_impact]
        df = df[df["impact_score"] >= min_score]

    output_path = args.output
    if args.format == "csv" or output_path.endswith(".csv"):
        df.to_csv(output_path, index=False)
    elif args.format == "parquet" or output_path.endswith(".parquet"):
        df.to_parquet(output_path, index=False)
    elif args.format == "json" or output_path.endswith(".json"):
        df.to_json(output_path, orient="records", indent=2)

    logger.info(f"Successfully exported {len(df)} records to {output_path}")

if __name__ == "__main__":
    main()