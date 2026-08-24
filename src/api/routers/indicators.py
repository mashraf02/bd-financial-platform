from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.engine import Connection

from src.api.dependencies import get_db_connection
from src.api.schemas import InflationOut, ReservesOut, TradeOut, RemittanceOut

router = APIRouter(prefix="/api", tags=["indicators"])

@router.get("/inflation", response_model=list[InflationOut])
def get_inflation(conn: Connection = Depends(get_db_connection)):
    query = text("""
        SELECT d.full_date, f.inflation_rate, f.measure_type
        FROM fact_inflation f
        JOIN dim_date d ON f.date_id = d.date_id
        ORDER BY d.full_date DESC
    """)
    return list(conn.execute(query).mappings().all())

@router.get("/reserves", response_model=list[ReservesOut])
def get_reserves(conn: Connection = Depends(get_db_connection)):
    query = text("""
        SELECT d.full_date, f.reserves_usd
        FROM fact_reserves f
        JOIN dim_date d ON f.date_id = d.date_id
        ORDER BY d.full_date DESC
    """)
    return list(conn.execute(query).mappings().all())

@router.get("/trade", response_model=list[TradeOut])
def get_trade(conn: Connection = Depends(get_db_connection)):
    query = text("""
        SELECT d.fiscal_year_label, f.exports_usd, f.imports_usd, f.trade_balance_usd
        FROM fact_trade f
        JOIN dim_date d ON f.date_id = d.date_id
        ORDER BY d.fiscal_year DESC
    """)
    return list(conn.execute(query).mappings().all())

@router.get("/remittance", response_model=list[RemittanceOut])
def get_remittance(conn: Connection = Depends(get_db_connection)):
    query = text("""
        SELECT d.full_date, f.remittance_usd
        FROM fact_remittance f
        JOIN dim_date d ON f.date_id = d.date_id
        ORDER BY d.full_date DESC
    """)
    return list(conn.execute(query).mappings().all())
