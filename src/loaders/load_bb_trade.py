import glob
import math
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from src.db import get_engine
from src.config import DATA_ROOT
from src.logger import get_logger

logger = get_logger(__name__)

def find_latest_file(source: str, filename_contains: str) -> Path:
    pattern = f"{DATA_ROOT}/{source}/**/*.xlsx"
    files = glob.glob(pattern, recursive=True)
    matches = [f for f in files if filename_contains in Path(f).name]
    if not matches:
        raise FileNotFoundError(f"No file containing '{filename_contains}' found under {DATA_ROOT}/{source}")
    latest = max(matches, key=lambda f: Path(f).stat().st_mtime)
    return Path(latest)

def is_missing(val) -> bool:
    if val is None:
        return True
    if isinstance(val, str) and val.strip() in ("…", "...", "-", ""):
        return True
    if isinstance(val, float) and math.isnan(val):
        return True
    return False

def get_source_id(engine, source_name: str) -> int:
    query = text("SELECT source_id FROM dim_source WHERE source_name = :s")
    with engine.connect() as conn:
        result = conn.execute(query, {"s": source_name}).fetchone()
    if result is None:
        raise ValueError(f"No dim_source row found for '{source_name}'")
    return result[0]

def get_date_id_for_fiscal_year(engine, fiscal_year_label: str) -> int | None:
    query = text("""
        SELECT date_id FROM dim_date
        WHERE fiscal_year_label = :label AND is_fiscal_year_end = TRUE
    """)
    with engine.connect() as conn:
        result = conn.execute(query, {"label": fiscal_year_label}).fetchone()
    return result[0] if result else None

def parse_table_ib(file_path: Path) -> pd.DataFrame:
    df = pd.read_excel(file_path, sheet_name="Table IB", header=None, skiprows=9)

    records = []
    for _, row in df.iterrows():
        period = row[0]
        if not isinstance(period, str) or "-" not in period:
            continue  # skip blank/trailing rows

        exports = row[27] if not is_missing(row[27]) else row[31]
        imports = row[28] if not is_missing(row[28]) else row[32]

        if is_missing(exports) or is_missing(imports):
            continue  # genuinely no usable trade figure for this year - skip, don't fabricate

        try:
            exports_usd = float(exports) * 1_000_000
            imports_usd = float(imports) * 1_000_000
        except (ValueError, TypeError):
            continue

        records.append({
            "fiscal_year_label": period,
            "exports_usd": exports_usd,
            "imports_usd": imports_usd,
            "trade_balance_usd": exports_usd - imports_usd,
        })

    return pd.DataFrame(records)

def load_bb_trade():
    engine = get_engine()
    source_id = get_source_id(engine, "bangladesh_bank")

    file_path = find_latest_file("bangladesh_bank", "time_series_data1972-2024")
    logger.info(f"Parsing trade data from {file_path}")

    df = parse_table_ib(file_path)
    logger.info(f"Parsed {len(df)} fiscal years with usable trade figures")

    rows = []
    skipped_no_date = 0
    for _, r in df.iterrows():
        date_id = get_date_id_for_fiscal_year(engine, r["fiscal_year_label"])
        if date_id is None:
            skipped_no_date += 1
            continue
        rows.append({
            "date_id": date_id,
            "source_id": source_id,
            "exports_usd": r["exports_usd"],
            "imports_usd": r["imports_usd"],
            "trade_balance_usd": r["trade_balance_usd"],
        })

    if not rows:
        logger.warning("No trade rows to insert")
        return

    insert_sql = text("""
        INSERT INTO fact_trade (date_id, source_id, exports_usd, imports_usd, trade_balance_usd)
        VALUES (:date_id, :source_id, :exports_usd, :imports_usd, :trade_balance_usd)
        ON CONFLICT (date_id, source_id) DO UPDATE
        SET exports_usd = EXCLUDED.exports_usd,
            imports_usd = EXCLUDED.imports_usd,
            trade_balance_usd = EXCLUDED.trade_balance_usd,
            loaded_at = now()
    """)

    with engine.begin() as conn:
        conn.execute(insert_sql, rows)

    logger.info(f"Inserted/updated {len(rows)} trade rows, skipped {skipped_no_date} (no matching fiscal year in dim_date)")

if __name__ == "__main__":
    load_bb_trade()

# DATA QUALITY NOTES (from initial load, Aug 2026):
# - FY1973-74 to FY1987-88: BB did not publish USD trade figures in this table for that era. Genuine gap.
# - FY2012-13, FY2013-14: import figure missing (exports present). Excluded to avoid a misleading partial row.
# - FY2021-22 onward: figures blank/provisional ('P' suffix) as of this file's publish date. Will populate
#   automatically once BB updates the source file and Phase 1 re-ingests it.
# Result: 31 of 51 possible fiscal years loaded with genuine, non-fabricated USD trade data.
