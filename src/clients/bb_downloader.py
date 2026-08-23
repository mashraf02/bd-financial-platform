import requests
from pathlib import Path
from datetime import datetime, timezone
from src.logger import get_logger

logger = get_logger(__name__)

def download_bb_excel(url: str, data_root: str = "./data/raw/bangladesh_bank"):
    now = datetime.now(timezone.utc)
    out_dir = Path(data_root) / now.strftime("%Y/%m/%d")
    out_dir.mkdir(parents=True, exist_ok=True)

    resp = requests.get(url, timeout=30)
    resp.raise_for_status()

    filename = url.split("/")[-1] or f"bb_data_{now.strftime('%Y%m%dT%H%M%S')}.xlsx"
    out_path = out_dir / filename
    out_path.write_bytes(resp.content)
    logger.info(f"Downloaded BB file to {out_path}")
    return out_path
