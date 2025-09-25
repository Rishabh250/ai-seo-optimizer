import logging
import os
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, connection_string: Optional[str] = None):
        if connection_string:
            self.connection_string = connection_string
        else:
            self.connection_string = self._build_connection_string()

        self.engine = create_engine(self.connection_string)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def _build_connection_string(self) -> str:
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        database = os.getenv("DB_NAME", "find_my_college")
        username = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD", "1234")

        return f"postgresql://{username}:{password}@{host}:{port}/{database}"

    @contextmanager
    def get_connection(self):
        conn = None
        try:
            conn = psycopg2.connect(self.connection_string)
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def execute_raw_query(self, query: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, params)

                    if query.strip().upper().startswith('SELECT'):
                        results = cur.fetchall()
                        return [dict(row) for row in results]
                    else:
                        conn.commit()
                        return [{"affected_rows": cur.rowcount}]

        except Exception as e:
            logger.error(f"Query execution error: {e}")
            raise

    def fetch_colleges_by_id(self, id: int) -> List[Dict[str, Any]]:
        query = """
            SELECT college_id, college_name, city, state, cleaned_raw
            FROM fmc_summary
            WHERE college_id = %(id)s AND cleaned_raw IS NOT NULL
        """

        return self.execute_raw_query(query, {"id": id})

    def custom_query(self, query: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        return self.execute_raw_query(query, params)


def get_db_manager(connection_string: Optional[str] = None) -> DatabaseManager:
    return DatabaseManager(connection_string)