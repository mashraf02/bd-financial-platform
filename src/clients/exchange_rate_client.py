from datetime import datetime, timezone
from src.clients.base_client import BaseAPIClient
from src.config import EXCHANGE_RATE_BASE_URL
from src.logger import get_logger

logger = get_logger(__name__)

class ExchangeRateClient(BaseAPIClient):
    def __init__(self):
        super().__init__(base_url=EXCHANGE_RATE_BASE_URL)

    def get_latest_rates(self, base_currency: str = "USD") -> dict:
        data = self._get(full_url=f"{self.base_url}/{base_currency}")
        if data.get("result") != "success":
            raise ValueError(f"API returned non-success result: {data.get('result')}")

        return {
            "base_currency": data["base_code"],
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "provider_last_update": data.get("time_last_update_utc"),
            "rates": data["rates"],
        }
