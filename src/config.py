import os
from dotenv import load_dotenv

load_dotenv()

DATA_ROOT = os.getenv("DATA_ROOT", "./data/raw")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
S3_BUCKET = os.getenv("S3_BUCKET")
AWS_REGION = os.getenv("AWS_REGION", "ap-southeast-1")

WORLD_BANK_BASE_URL = "https://api.worldbank.org/v2"
EXCHANGE_RATE_BASE_URL = "https://open.er-api.com/v6/latest"

WORLD_BANK_INDICATORS = {
    "inflation": "FP.CPI.TOTL.ZG",
    "reserves": "FI.RES.TOTL.CD",
    "trade_balance": "NE.RSB.GNFS.ZS",
    "remittance": "BX.TRF.PWKR.CD.DT",
    "gdp_growth": "NY.GDP.MKTP.KD.ZG",
}
