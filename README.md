# Forex Factory Economic Calendar Scraper
A Python scraper I have designed to extract economic calendar events from Forex Factory while handling bot protections like Cloudflare.

## Features
- **Cloudflare Bypass & Caching:** It uses `cloudscraper` to try and mimic real browser TLS fingerprints and it automatically caches raw HTML locally.
- **Local Fallback Mode:** It falls back to local HTML snapshots if IP rate-limiting or blocks do happen, and thus it ensures uninterrupted development and testing.
- **Structured Parsing:** Extracts listed macroeconomic indicators (Date, Time, Currency, Impact Level, Event Title, Actual, Forecast, and Previous values).
- **Idempotent Storage:** Exports data into CSV formats and appends data to a historical dataset.

