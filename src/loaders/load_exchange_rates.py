import json
import glob
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from src.db import get_engine
from src.config import DATA_ROOT
from src.logger import get_logger

logger = get_logger(__name__)

def find_latest_file(source: str) -> Path:
    pattern = f"{DATA_ROOT}/{source}/**/*.json"
    files = glob.glob(pattern, recursive=True)
    if not files:
        raise FileNotFoundError(f"No files found for source '{source}' under {DATA_ROOT}")
    latest = max(files, key=lambda f: Path(f).stat().st_mtime)
    return Path(latest)

def load_currency_lookup(engine) -> dict:
    df = pd.read_sql("SELECT currency_id, currency_code FROM dim_currency", engine)
    return dict(zip(df["currency_code"], df["currency_id"]))

def get_date_id(engine, target_date) -> int:
    query = text("SELECT date_id FROM dim_date WHERE full_date = :d")
    with engine.connect() as conn:
        result = conn.execute(query, {"d": target_date}).fetchone()
    if result is None:
        raise ValueError(f"No dim_date row found for {target_date}")
    return result[0]

def get_source_id(engine, source_name: str) -> int:
    query = text("SELECT source_id FROM dim_source WHERE source_name = :s")
    with engine.connect() as conn:
        result = conn.execute(query, {"s": source_name}).fetchone()
    if result is None:
        raise ValueError(f"No dim_source row found for '{source_name}'")
    return result[0]

def load_exchange_rates():
    engine = get_engine()

    file_path = find_latest_file("exchange_rates")
    logger.info(f"Loading exchange rates from {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    fetched_at = datetime.fromisoformat(data["fetched_at"])
    target_date = fetched_at.date()

    currency_lookup = load_currency_lookup(engine)
    date_id = get_date_id(engine, target_date)
    source_id = get_source_id(engine, "open_er_api")

    rows = []
    skipped = 0
    for code, rate in data["rates"].items():
        currency_id = currency_lookup.get(code)
        if currency_id is None:
            skipped += 1
            continue
        rows.append({
            "date_id": date_id,
            "currency_id": currency_id,
            "source_id": source_id,
            "rate_to_usd": rate,
            "rate_type": "live",
        })

    logger.info(f"Matched {len(rows)} currencies, skipped {skipped} (not in dim_currency)")

    if not rows:
        logger.warning("No rows to insert")
        return

    df = pd.DataFrame(rows)

    insert_sql = text("""
        INSERT INTO fact_exchange_rate (date_id, currency_id, source_id, rate_to_usd, rate_type)
        VALUES (:date_id, :currency_id, :source_id, :rate_to_usd, :rate_type)
        ON CONFLICT (date_id, currency_id, source_id, rate_type) DO UPDATE
        SET rate_to_usd = EXCLUDED.rate_to_usd, loaded_at = now()
    """)

    with engine.begin() as conn:
        conn.execute(insert_sql, df.to_dict(orient="records"))

    logger.info(f"Inserted/updated {len(rows)} exchange rate rows")

if __name__ == "__main__":
    load_exchange_rates()
