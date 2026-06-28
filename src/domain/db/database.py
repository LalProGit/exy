from __future__ import annotations
import sqlite3
import sqlite_vec
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:

    def __init__(self, db_path: str):
        self.db_path = db_path
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(db_path)
        try:
            conn.enable_load_extension(True)
            sqlite_vec.load(conn)
            conn.enable_load_extension(False)

            yield

        except Exception as e:
            logger.error(f"Database connection error {e}")
            raise
        
        finally:
            conn.close()