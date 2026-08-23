import pandas as pd
from datetime import date
from src.db import get_engine
from src.logger import get_logger

logger = get_logger(__name__)

def bangladesh_fiscal_year(d: date) -> tuple[int, str]:
    """
    Bangladesh fiscal year runs July 1 - June 30.
    A date in Jul-Dec belongs to the FY that ENDS the following June.
    A date in Jan-Jun belongs to the FY that ends THIS June.
    Returns (fiscal_year_ending, label) e.g. (1974, '1973-74')
    """
    if d.month >= 7:
        start_year = d.year
        end_year = d.year + 1
    else:
        start_year = d.year - 1
        end_year = d.year
    label = f"{start_year}-{str(end_year)[-2:]}"
    return end_year, label

def build_dim_date(start_year: int = 1971, end_year: int = 2027) -> pd.DataFrame:
    dates = pd.date_range(start=f"{start_year}-01-01", end=f"{end_year}-12-31", freq="D")

    rows = []
    for d in dates:
        d_date = d.date()
        fy, fy_label = bangladesh_fiscal_year(d_date)
        is_fy_end = (d_date.month == 6 and d_date.day == 30)
        rows.append({
            "full_date": d_date,
            "calendar_year": d_date.year,
            "calendar_month": d_date.month,
            "calendar_day": d_date.day,
            "quarter": (d_date.month - 1) // 3 + 1,
            "fiscal_year": fy,
            "fiscal_year_label": fy_label,
            "is_fiscal_year_end": is_fy_end,
        })

    return pd.DataFrame(rows)

def main():
    logger.info("Building dim_date")
    df = build_dim_date()
    logger.info(f"Generated {len(df)} date rows")

    engine = get_engine()
    df.to_sql("dim_date", engine, if_exists="append", index=False, method="multi", chunksize=5000)
    logger.info("dim_date populated successfully")

if __name__ == "__main__":
    main()
