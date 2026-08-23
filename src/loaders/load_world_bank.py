import json
import glob
from datetime import date
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from src.db import get_engine
from src.config import DATA_ROOT
from src.logger import get_logger

logger = get_logger(__name__)

# Maps World Bank source folder name -> (target table, value column name)
INDICATOR_TABLE_MAP = {
    "inflation": ("fact_inflation", "inflation_rate"),
    "reserves": ("fact_reserves", "reserves_usd"),
    "trade_balance": ("fact_trade", None),  # special-cased below
    "remittance": ("fact_remittance", "remittance_usd"),
}

def find_latest_file(source: str) -> Path:
    pattern = f"{DATA_ROOT}/{source}/**/*.json"
    files = glob.glob(pattern, recursive=True)
    if not files:
        raise FileNotFoundError(f"No files found for source '{source}' under {DATA_ROOT}")
    latest = max(files, key=lambda f: Path(f).stat().st_mtime)
    return Path(latest)

def get_date_id_for_year(engine, year: int) -> int | None:
    target_date = date(year, 12, 31)
    query = text("SELECT date_id FROM dim_date WHERE full_date = :d")
    with engine.connect() as conn:
        result = conn.execute(query, {"d": target_date}).fetchone()
    return result[0] if result else None

def get_source_id(engine, source_name: str) -> int:
    query = text("SELECT source_id FROM dim_source WHERE source_name = :s")
    with engine.connect() as conn:
        result = conn.execute(query, {"s": source_name}).fetchone()
    if result is None:
        raise ValueError(f"No dim_source row found for '{source_name}'")
    return result[0]

def load_indicator(engine, source_folder: str, table_name: str, value_col: str, source_id: int):
    file_path = find_latest_file(source_folder)
    logger.info(f"Loading {source_folder} from {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    rows = []
    skipped = 0
    for rec in records:
        try:
            year = int(rec["year"])
        except (ValueError, TypeError):
            skipped += 1
            continue

        date_id = get_date_id_for_year(engine, year)
        if date_id is None:
            skipped += 1
            continue

        if rec["value"] is None:
            skipped += 1
            continue

        row = {"date_id": date_id, "source_id": source_id}
        if table_name == "fact_inflation":
            row["inflation_rate"] = rec["value"]
            row["measure_type"] = "CPI_annual_pct"
        elif table_name == "fact_reserves":
            row["reserves_usd"] = rec["value"]
        elif table_name == "fact_remittance":
            row["remittance_usd"] = rec["value"]
        rows.append(row)

    if not rows:
        logger.warning(f"No rows to insert for {source_folder}")
        return 0

    df = pd.DataFrame(rows)

    if table_name == "fact_inflation":
        insert_sql = text("""
            INSERT INTO fact_inflation (date_id, source_id, inflation_rate, measure_type)
            VALUES (:date_id, :source_id, :inflation_rate, :measure_type)
            ON CONFLICT (date_id, source_id, measure_type) DO UPDATE
            SET inflation_rate = EXCLUDED.inflation_rate, loaded_at = now()
        """)
    elif table_name == "fact_reserves":
        insert_sql = text("""
            INSERT INTO fact_reserves (date_id, source_id, reserves_usd)
            VALUES (:date_id, :source_id, :reserves_usd)
            ON CONFLICT (date_id, source_id) DO UPDATE
            SET reserves_usd = EXCLUDED.reserves_usd, loaded_at = now()
        """)
    elif table_name == "fact_remittance":
        insert_sql = text("""
            INSERT INTO fact_remittance (date_id, source_id, remittance_usd)
            VALUES (:date_id, :source_id, :remittance_usd)
            ON CONFLICT (date_id, source_id) DO UPDATE
            SET remittance_usd = EXCLUDED.remittance_usd, loaded_at = now()
        """)

    with engine.begin() as conn:
        conn.execute(insert_sql, df.to_dict(orient="records"))

    logger.info(f"{source_folder}: inserted/updated {len(rows)}, skipped {skipped}")
    return len(rows)

def load_trade_balance(engine, source_id: int):
    """Trade balance from World Bank is % of GDP, not USD - not directly usable for
    fact_trade (which expects exports/imports/balance in USD). Log and skip for now;
    we'll get real trade USD figures from the Bangladesh Bank Excel files instead."""
    logger.info("Skipping trade_balance World Bank load (unit mismatch: %% of GDP, not USD) - will source from BB instead")

def main():
    engine = get_engine()
    source_id = get_source_id(engine, "world_bank")

    load_indicator(engine, "inflation", "fact_inflation", "inflation_rate", source_id)
    load_indicator(engine, "reserves", "fact_reserves", "reserves_usd", source_id)
    load_indicator(engine, "remittance", "fact_remittance", "remittance_usd", source_id)
    load_trade_balance(engine, source_id)

if __name__ == "__main__":
    main()
