import json
from datetime import datetime, timezone
from pathlib import Path
from src.config import DATA_ROOT
from src.logger import get_logger

logger = get_logger(__name__)

class RawDataWriter:
    def __init__(self, data_root: str = DATA_ROOT):
        self.data_root = Path(data_root)

    def write(self, source: str, payload) -> Path:
        now = datetime.now(timezone.utc)
        partition = now.strftime("%Y/%m/%d")
        out_dir = self.data_root / source / partition
        out_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{source}_{now.strftime('%Y%m%dT%H%M%S')}.json"
        out_path = out_dir / filename

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        logger.info(f"Wrote {out_path}")
        return out_path
