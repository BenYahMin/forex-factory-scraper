import re
from bs4 import BeautifulSoup

class ForexFactoryParser:
    def parse_html(self, html: str) -> list[dict]:
        """
        Parses Forex Factory calendar HTML table with state tracking for missing date/time cells.
        """
        soup = BeautifulSoup(html, "html.parser")
        events = []

        table = soup.find("table", class_="calendar__table")
        if not table:
            return events

        current_date = None
        current_time = None

        for row in table.find_all("tr", class_="calendar__row"):
            # Forward-fill Date
            date_cell = row.find("td", class_="calendar__date")
            if date_cell and date_cell.text.strip():
                current_date = re.sub(r'\s+', ' ', date_cell.text).strip()

            # Forward-fill Time
            time_cell = row.find("td", class_="calendar__time")
            if time_cell and time_cell.text.strip():
                current_time = re.sub(r'\s+', ' ', time_cell.text).strip()

            # Extract Currency
            currency_cell = row.find("td", class_="calendar__currency")
            currency = currency_cell.text.strip() if currency_cell else None

            if not currency:
                continue

            # Extract Event Name
            event_cell = row.find("td", class_="calendar__event")
            event_name = event_cell.text.strip() if event_cell else None

            # Extract Impact
            impact_cell = row.find("td", class_="calendar__impact")
            impact = self._extract_impact(impact_cell)

            # Extract Metrics
            actual = self._get_cell_text(row, "calendar__actual")
            forecast = self._get_cell_text(row, "calendar__forecast")
            previous = self._get_cell_text(row, "calendar__previous")

            events.append({
                "date": current_date,
                "time": current_time,
                "currency": currency,
                "impact": impact,
                "event": event_name,
                "actual_raw": actual,
                "forecast_raw": forecast,
                "previous_raw": previous
            })

        return events

    def _get_cell_text(self, row, class_name: str) -> str | None:
        cell = row.find("td", class_=class_name)
        return cell.text.strip() if cell else None

    def _extract_impact(self, impact_cell) -> str:
        if not impact_cell:
            return "Unknown"
        span = impact_cell.find("span", class_=re.compile("impact"))
        if span:
            classes = span.get("class", [])
            for cls in classes:
                if "red" in cls: return "High"
                if "ora" in cls: return "Medium"
                if "yel" in cls: return "Low"
                if "gra" in cls: return "Non-Economic"
        return "Unknown"