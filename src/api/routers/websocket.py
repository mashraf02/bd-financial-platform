import asyncio
import json
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import text

from src.db import get_engine
from src.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

POLL_INTERVAL_SECONDS = 5

def fetch_latest_streamed_rates() -> list[dict]:
    engine = get_engine()
    query = text("""
        SELECT c.currency_code, f.rate_to_usd, f.loaded_at
        FROM fact_exchange_rate f
        JOIN dim_currency c ON f.currency_id = c.currency_id
        WHERE f.rate_type = 'streamed_live'
        ORDER BY f.loaded_at DESC
    """)
    with engine.connect() as conn:
        rows = conn.execute(query).mappings().all()

    seen = set()
    latest = []
    for row in rows:
        if row["currency_code"] not in seen:
            seen.add(row["currency_code"])
            latest.append({
                "currency_code": row["currency_code"],
                "rate_to_usd": float(row["rate_to_usd"]),
                "loaded_at": row["loaded_at"].isoformat(),
            })
    return latest

@router.websocket("/ws/exchange-rates")
async def websocket_exchange_rates(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket client connected")
    last_sent_timestamp = None

    try:
        while True:
            rates = fetch_latest_streamed_rates()
            current_timestamp = rates[0]["loaded_at"] if rates else None

            if current_timestamp and current_timestamp != last_sent_timestamp:
                await websocket.send_json({
                    "type": "rate_update",
                    "data": rates,
                    "server_time": datetime.utcnow().isoformat(),
                })
                last_sent_timestamp = current_timestamp

            await asyncio.sleep(POLL_INTERVAL_SECONDS)

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
