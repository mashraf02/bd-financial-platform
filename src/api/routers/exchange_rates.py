from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.engine import Connection

from src.api.dependencies import get_db_connection
from src.api.schemas import ExchangeRateOut

router = APIRouter(prefix="/api/exchange-rates", tags=["exchange-rates"])

@router.get("", response_model=list[ExchangeRateOut])
def get_latest_exchange_rates(
    rate_type: str = Query(default="live", description="'live', 'streamed_live', etc."),
    conn: Connection = Depends(get_db_connection),
):
    query = text("""
        SELECT c.currency_code, c.currency_name, f.rate_to_usd, f.rate_type, d.full_date
        FROM fact_exchange_rate f
        JOIN dim_currency c ON f.currency_id = c.currency_id
        JOIN dim_date d ON f.date_id = d.date_id
        WHERE f.rate_type = :rate_type
        ORDER BY d.full_date DESC, c.currency_code
    """)
    rows = conn.execute(query, {"rate_type": rate_type}).mappings().all()
    return list(rows)

@router.get("/{currency_code}", response_model=list[ExchangeRateOut])
def get_exchange_rate_for_currency(
    currency_code: str,
    conn: Connection = Depends(get_db_connection),
):
    query = text("""
        SELECT c.currency_code, c.currency_name, f.rate_to_usd, f.rate_type, d.full_date
        FROM fact_exchange_rate f
        JOIN dim_currency c ON f.currency_id = c.currency_id
        JOIN dim_date d ON f.date_id = d.date_id
        WHERE UPPER(c.currency_code) = UPPER(:code)
        ORDER BY d.full_date DESC
    """)
    rows = conn.execute(query, {"code": currency_code}).mappings().all()
    return list(rows)
