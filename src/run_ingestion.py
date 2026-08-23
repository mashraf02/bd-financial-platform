from src.clients.exchange_rate_client import ExchangeRateClient
from src.clients.world_bank_client import WorldBankClient
from src.storage.s3_writer import RawDataWriter
from src.config import WORLD_BANK_INDICATORS
from src.logger import get_logger

logger = get_logger("run_ingestion")

def ingest_exchange_rates(writer: RawDataWriter):
    try:
        client = ExchangeRateClient()
        data = client.get_latest_rates("USD")
        writer.write("exchange_rates", data)
    except Exception as e:
        logger.error(f"Exchange rate ingestion failed: {e}", exc_info=True)

def ingest_world_bank_indicators(writer: RawDataWriter):
    client = WorldBankClient(country_code="bgd")
    for name, code in WORLD_BANK_INDICATORS.items():
        try:
            records = client.get_indicator(code)
            if records:
                writer.write(name, records)
            else:
                logger.warning(f"No records returned for {name} ({code})")
        except Exception as e:
            logger.error(f"World Bank ingestion failed for {name}: {e}", exc_info=True)

def main():
    writer = RawDataWriter()
    logger.info("Starting Phase 1 ingestion run")
    ingest_exchange_rates(writer)
    ingest_world_bank_indicators(writer)
    logger.info("Ingestion run complete")

if __name__ == "__main__":
    main()
