from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.engine import Connection

from src.api.dependencies import get_db_connection
from src.api.schemas import DashboardSummary

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("", response_model=DashboardSummary)
def get_dashboard_summary(conn: Connection = Depends(get_db_connection)):
    usd_bdt = conn.execute(text("""
        SELECT f.rate_to_usd FROM fact_exchange_rate f
        JOIN dim_currency c ON f.currency_id = c.currency_id
        JOIN dim_date d ON f.date_id = d.date_id
        WHERE c.currency_code = 'BDT'
        ORDER BY d.full_date DESC, f.loaded_at DESC LIMIT 1
    """)).scalar()

    inflation = conn.execute(text("""
        SELECT f.inflation_rate FROM fact_inflation f
        JOIN dim_date d ON f.date_id = d.date_id
        ORDER BY d.full_date DESC LIMIT 1
    """)).scalar()

    reserves = conn.execute(text("""
        SELECT f.reserves_usd FROM fact_reserves f
        JOIN dim_date d ON f.date_id = d.date_id
        ORDER BY d.full_date DESC LIMIT 1
    """)).scalar()

    remittance = conn.execute(text("""
        SELECT f.remittance_usd FROM fact_remittance f
        JOIN dim_date d ON f.date_id = d.date_id
        ORDER BY d.full_date DESC LIMIT 1
    """)).scalar()

    return DashboardSummary(
        latest_usd_bdt_rate=usd_bdt,
        latest_inflation_rate=inflation,
        latest_reserves_usd=reserves,
        latest_remittance_usd=remittance,
    )
