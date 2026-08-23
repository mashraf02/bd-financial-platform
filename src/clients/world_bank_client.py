from src.clients.base_client import BaseAPIClient
from src.config import WORLD_BANK_BASE_URL
from src.logger import get_logger

logger = get_logger(__name__)

class WorldBankClient(BaseAPIClient):
    def __init__(self, country_code: str = "bgd"):
        super().__init__(base_url=WORLD_BANK_BASE_URL)
        self.country_code = country_code

    def get_indicator(self, indicator_code: str, per_page: int = 100) -> list:
        path = f"country/{self.country_code}/indicator/{indicator_code}"
        params = {"format": "json", "per_page": per_page}
        data = self._get(path=path, params=params)

        if not isinstance(data, list) or len(data) < 2:
            logger.warning(f"Unexpected response shape for {indicator_code}")
            return []

        records = data[1] or []
        return [
            {
                "indicator": r["indicator"]["value"],
                "indicator_code": indicator_code,
                "country": r["country"]["value"],
                "year": r["date"],
                "value": r["value"],
            }
            for r in records
            if r["value"] is not None
        ]
