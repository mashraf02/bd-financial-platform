from datetime import date
from pydantic import BaseModel

class ExchangeRateOut(BaseModel):
    currency_code: str
    currency_name: str
    rate_to_usd: float
    rate_type: str
    full_date: date

class InflationOut(BaseModel):
    full_date: date
    inflation_rate: float
    measure_type: str

class ReservesOut(BaseModel):
    full_date: date
    reserves_usd: float

class TradeOut(BaseModel):
    fiscal_year_label: str
    exports_usd: float
    imports_usd: float
    trade_balance_usd: float

class RemittanceOut(BaseModel):
    full_date: date
    remittance_usd: float

class DashboardSummary(BaseModel):
    latest_usd_bdt_rate: float | None
    latest_inflation_rate: float | None
    latest_reserves_usd: float | None
    latest_remittance_usd: float | None
