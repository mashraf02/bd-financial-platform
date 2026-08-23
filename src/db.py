from sqlalchemy import create_engine
from src.config import DATABASE_URL
from src.logger import get_logger

logger = get_logger(__name__)

_engine = None

def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(DATABASE_URL)
        logger.info("Database engine created")
    return _engine
