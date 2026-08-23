import pandas as pd
from src.db import get_engine
from src.logger import get_logger

logger = get_logger(__name__)

CURRENCIES = [
    ("USD", "US Dollar"),
    ("BDT", "Bangladeshi Taka"),
    ("EUR", "Euro"),
    ("GBP", "British Pound Sterling"),
    ("INR", "Indian Rupee"),
    ("JPY", "Japanese Yen"),
    ("CNY", "Chinese Yuan"),
    ("AUD", "Australian Dollar"),
    ("CAD", "Canadian Dollar"),
    ("SGD", "Singapore Dollar"),
    ("MYR", "Malaysian Ringgit"),
    ("SAR", "Saudi Arabian Riyal"),
    ("AED", "UAE Dirham"),
    ("SDR", "Special Drawing Rights"),
]

SOURCES = [
    ("open_er_api", "api", "https://open.er-api.com/v6/latest"),
    ("world_bank", "api", "https://api.worldbank.org/v2"),
    ("bangladesh_bank", "file", "https://www.bb.org.bd/econdata"),
]

def main():
    engine = get_engine()

    df_currency = pd.DataFrame(CURRENCIES, columns=["currency_code", "currency_name"])
    df_source = pd.DataFrame(SOURCES, columns=["source_name", "source_type", "source_url"])

    df_currency.to_sql("dim_currency", engine, if_exists="append", index=False)
    logger.info(f"Inserted {len(df_currency)} currencies")

    df_source.to_sql("dim_source", engine, if_exists="append", index=False)
    logger.info(f"Inserted {len(df_source)} sources")

if __name__ == "__main__":
    main()
