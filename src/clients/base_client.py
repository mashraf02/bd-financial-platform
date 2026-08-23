import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from src.logger import get_logger

logger = get_logger(__name__)

class APIClientError(Exception):
    pass

class BaseAPIClient:
    def __init__(self, base_url: str, timeout: int = 15):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()

    @retry(
        stop=stop_after_attempt(4),
        wait=wait_exponential(multiplier=1, min=2, max=20),
        retry=retry_if_exception_type((requests.ConnectionError, requests.Timeout)),
        reraise=True,
    )
    def _get(self, path: str = "", params: dict = None, full_url: str = None):
        url = full_url or f"{self.base_url}/{path}"
        logger.info(f"GET {url} params={params}")
        try:
            resp = self.session.get(url, params=params, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.HTTPError as e:
            logger.error(f"HTTP error for {url}: {e}")
            raise APIClientError(f"HTTP error: {e}") from e
        except ValueError as e:
            logger.error(f"Invalid JSON from {url}: {e}")
            raise APIClientError(f"Invalid JSON: {e}") from e
