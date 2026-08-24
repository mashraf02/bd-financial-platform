import json
import time
from datetime import datetime, timezone

from kafka import KafkaProducer
from kafka.errors import KafkaError

from src.clients.exchange_rate_client import ExchangeRateClient
from src.logger import get_logger

logger = get_logger(__name__)

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC = "exchange_rates_stream"
POLL_INTERVAL_SECONDS = 30

def create_producer() -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        retries=3,
        acks="all",
    )

def run_producer():
    producer = create_producer()
    client = ExchangeRateClient()
    logger.info(f"Producer started - publishing to topic '{TOPIC}' every {POLL_INTERVAL_SECONDS}s")

    while True:
        try:
            data = client.get_latest_rates("USD")
            message = {
                "base_currency": data["base_currency"],
                "fetched_at": data["fetched_at"],
                "published_at": datetime.now(timezone.utc).isoformat(),
                "rates": data["rates"],
            }

            future = producer.send(TOPIC, value=message)
            record_metadata = future.get(timeout=10)
            logger.info(
                f"Published message to partition {record_metadata.partition} "
                f"at offset {record_metadata.offset} - base={message['base_currency']}"
            )

        except KafkaError as e:
            logger.error(f"Kafka publish failed: {e}")
        except Exception as e:
            logger.error(f"Producer error: {e}", exc_info=True)

        time.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    run_producer()
