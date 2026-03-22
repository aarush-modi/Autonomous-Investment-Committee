import os
from fredapi import Fred
from datetime import date
from src.data.providers.base import EconomicDataProvider


class FredProvider(EconomicDataProvider):
    def __init__(self):
        api_key = os.getenv("FRED_API_KEY")
        if not api_key:
            raise ValueError("FRED_API_KEY environment variable not set")
        self.client = Fred(api_key=api_key)

    def get_series(self, series_id: str, start: date, end: date) -> dict:
        data = self.client.get_series(series_id, observation_start=start, observation_end=end)
        return {
            "series_id": series_id,
            "title": self._get_series_name(series_id),
            "data": {str(d): float(v) for d, v in data.dropna().items()},
        }

    def _get_series_name(self, series_id: str) -> str:
        try:
            info = self.client.get_series_info(series_id)
            return info["title"]
        except Exception:
            return series_id
