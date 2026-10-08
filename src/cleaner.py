import re
from datetime import datetime

class ForexFactoryCleaner:
    IMPACT_MAP = {
        "High": 3,
        "Medium": 2,
        "Low": 1,
        "Non-Economic": 0,
        "Unknown": -1
    }

    MULTIPLIERS = {
        'K': 1e3,
        'M': 1e6,
        'B': 1e9,
        'T': 1e12
    }

    @classmethod
    def parse_metric(cls, raw_val: str) -> float | None:
        if not raw_val or raw_val.strip() in ['-', '--', '', 'N/A']:
            return None

        val = raw_val.strip().upper()
        is_negative = False

        if val.startswith('(') and val.endswith(')'):
            is_negative = True
            val = val[1:-1].strip()
        elif val.startswith('-'):
            is_negative = True
            val = val[1:].strip()

        is_percent = '%' in val
        val = re.sub(r'[^0-9\.KMBT]', '', val)

        if not val:
            return None

        multiplier = 1.0
        if val[-1] in cls.MULTIPLIERS:
            multiplier = cls.MULTIPLIERS[val[-1]]
            val = val[:-1]

        try:
            numeric_val = float(val) * multiplier
            if is_percent:
                numeric_val /= 100.0
            return -numeric_val if is_negative else numeric_val
        except ValueError:
            return None

    @classmethod
    def parse_datetime(cls, date_str: str, time_str: str, year: int = 2026) -> str | None:
        if not date_str:
            return None

        time_part = "00:00" if not time_str or time_str.lower() in ['all day', 'tentative'] else time_str.strip()
        cleaned_date = re.sub(r'^[A-Za-z]{3}\s+', '', date_str.strip())
        full_str = f"{cleaned_date} {year} {time_part}"

        for fmt in ("%b %d %Y %I:%M%p", "%b %d %Y %H:%M"):
            try:
                dt = datetime.strptime(full_str, fmt)
                return dt.isoformat()
            except ValueError:
                continue

        return None

    def clean_event(self, raw_event: dict, year: int = 2026) -> dict:
        impact_label = raw_event.get("impact", "Unknown")
        return {
            "timestamp": self.parse_datetime(raw_event.get("date"), raw_event.get("time"), year=year),
            "date_raw": raw_event.get("date"),
            "time_raw": raw_event.get("time"),
            "currency": raw_event.get("currency"),
            "event": raw_event.get("event"),
            "impact_label": impact_label,
            "impact_score": self.IMPACT_MAP.get(impact_label, -1),
            "actual": self.parse_metric(raw_event.get("actual_raw")),
            "forecast": self.parse_metric(raw_event.get("forecast_raw")),
            "previous": self.parse_metric(raw_event.get("previous_raw")),
            "actual_raw": raw_event.get("actual_raw"),
            "forecast_raw": raw_event.get("forecast_raw"),
            "previous_raw": raw_event.get("previous_raw"),
        }