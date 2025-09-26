"""
Service layer for campus infrastructure data operations.
"""
from typing import Optional

from ..models.campus import CampusData
from ..utils.exceptions import CollegeNotFoundError
from ..utils.logging_config import get_logger
from .manager import get_db_manager

logger = get_logger(__name__)


class CampusService:
    """Service for managing campus infrastructure data operations."""

    def __init__(self):
        self.db = get_db_manager()

    def get_campus_by_college_id(self, college_id: int) -> CampusData:
        """Get campus infrastructure data for a college."""
        try:
            query = """
                SELECT category3_raw
                FROM fmc_infrastructure
                WHERE college_id = %(college_id)s AND category3_raw IS NOT NULL
                ORDER BY id DESC
                LIMIT 1
            """
            
            results = self.db.execute_raw_query(query, {"college_id": college_id})
            
            if not results:
                logger.warning(f"No campus data found for college ID {college_id}")
                raise CollegeNotFoundError(str(college_id), "ID")
            
            raw_output = results[0].get('category3_raw', '{}')
            
            try:
                campus_data = CampusData.from_raw_output(raw_output)
                logger.info(f"Successfully retrieved campus data for college ID {college_id}")
                return campus_data
            except Exception as e:
                logger.error(f"Error parsing campus data for college {college_id}: {e}")
                raise Exception(f"Failed to parse campus data: {e}")
            
        except CollegeNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving campus data for college ID {college_id}: {e}")
            raise Exception(f"Failed to retrieve campus data: {e}")
