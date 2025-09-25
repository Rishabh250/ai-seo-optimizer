"""
Service layer for fees data operations.
"""
from typing import List

from ..models.fees import FeesData
from ..utils.exceptions import CollegeNotFoundError
from ..utils.logging_config import get_logger
from .manager import get_db_manager

logger = get_logger(__name__)

class FeesService:
    """Service for managing fees data operations."""

    def __init__(self):
        self.db = get_db_manager()

    def get_fees_by_college_id(self, college_id: int, limit: int = 10) -> List[FeesData]:
        try:
            query = """
                SELECT degree_name, raw_output
                FROM fmc_degree_fees
                WHERE college_id = %(college_id)s AND raw_output IS NOT NULL
                ORDER BY id DESC
                LIMIT %(limit)s
            """
            
            results = self.db.execute_raw_query(query, {"college_id": college_id, "limit": limit})
            
            if not results:
                logger.warning(f"No fees data found for college ID {college_id}")
                raise CollegeNotFoundError(str(college_id), "ID")
            
            fees_data_list = []
            for row in results:
                degree_name = row.get('degree_name', '')
                raw_output = row.get('raw_output', '{}')
                
                try:
                    fees_data = FeesData.from_raw_output(degree_name, raw_output)
                    fees_data_list.append(fees_data)
                    logger.debug(f"Successfully parsed fees data for degree: {degree_name}")
                except Exception as e:
                    logger.error(f"Error parsing fees data for degree {degree_name}: {e}")
                    continue
            
            if not fees_data_list:
                logger.warning(f"No valid fees data could be parsed for college ID {college_id}")
                raise CollegeNotFoundError(str(college_id), "ID")
            
            logger.info(f"Successfully retrieved {len(fees_data_list)} fees records for college ID {college_id}")
            return fees_data_list
            
        except CollegeNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving fees data for college ID {college_id}: {e}")
            raise Exception(f"Failed to retrieve fees data: {e}")