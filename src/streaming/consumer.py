import json
from datetime import datetime

from kafka import KafkaConsumer
from sqlalchemy import text

from src.db import get_engine
from src.logger import get_logger

logger = get_logger(__name__)

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC = "exchange_rates_stream"
CONSUMER_GROUP = "bd_platform_consumer"

def create_consumer() -> KafkaConsumer:
    return KafkaConsumer(
        TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=CONSUMER_GROUP,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
    )

def load_currency_lookup(engine) -> dict:
    import pandas as pd
    df = pd.read_sql("SELECT currency_id, currency_code FROM dim_currency", engine)
    return dict(zip(df["currency_code"], df["currency_id"]))

def get_date_id(engine, target_date) -> int | None:
    query = text("SELECT date_id FROM dim_date WHERE full_date = :d")
    with engine.connect() as conn:
        result = conn.execute(query, {"d": target_date}).fetchone()
    return result[0] if result else None

def get_source_id(engine, source_name: str) -> int:
    query = text("SELECT source_id FROM dim_source WHERE source_name = :s")
    with engine.connect() as conn:
        result = conn.execute(query, {"s": source_name}).fetchone()
    return result[0]

def process_message(engine, message: dict, currency_lookup: dict, source_id: int):
    fetched_at = datetime.fromisoformat(message["fetched_at"])
    target_date = fetched_at.date()
    date_id = get_date_id(engine, target_date)

    if date_id is None:
        logger.warning(f"No dim_date row for {target_date}, skipping message")
        return

    rows = []
    for code, rate in message["rates"].items():
        currency_id = currency_lookup.get(code)
        if currency_id is None:
            continue
        rows.append({
            "date_id": date_id,
            "currency_id": currency_id,
            "source_id": source_id,
            "rate_to_usd": rate,
            "rate_type": "streamed_live",
        })

    if not rows:
        return

    insert_sql = text("""
        INSERT INTO fact_exchange_rate (date_id, currency_id, source_id, rate_to_usd, rate_type)
        VALUES (:date_id, :currency_id, :source_id, :rate_to_usd, :rate_type)
        ON CONFLICT (date_id, currency_id, source_id, rate_type) DO UPDATE
        SET rate_to_usd = EXCLUDED.rate_to_usd, loaded_at = now()
    """)

    with engine.begin() as conn:
        conn.execute(insert_sql, rows)

    logger.info(f"Wrote {len(rows)} streamed rates for {target_date} (published_at={message['published_at']})")

def run_consumer():
    engine = get_engine()
    consumer = create_consumer()
    currency_lookup = load_currency_lookup(engine)
    source_id = get_source_id(engine, "open_er_api")

    logger.info(f"Consumer started - listening on topic '{TOPIC}' as group '{CONSUMER_GROUP}'")

    for message in consumer:
        try:
            process_message(engine, message.value, currency_lookup, source_id)
        except Exception as e:
            logger.error(f"Failed to process message: {e}", exc_info=True)

if __name__ == "__main__":
    run_consumer()
