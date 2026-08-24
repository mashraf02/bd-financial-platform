from sqlalchemy import text
from src.db import get_engine

def get_db_connection():
    engine = get_engine()
    conn = engine.connect()
    try:
        yield conn
    finally:
        conn.close()
