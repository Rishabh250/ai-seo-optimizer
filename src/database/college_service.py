"""
Service layer for college data operations.
"""
import json
from typing import Optional

from ..models.college import College, CollegeData
from ..utils.logging_config import get_logger
from .manager import get_db_manager

logger = get_logger(__name__)

class CollegeService:
    """Service for managing college data operations."""

    def __init__(self):
        self.db = get_db_manager()

    def get_college_by_id(self, college_id: int) -> Optional[College]:
        """Retrieve and process college data by ID."""
        try:
            results = self.db.fetch_colleges_by_id(college_id)
            
            if not results:
                logger.warning(f"No college found with ID {college_id}")
                return None
            
            row = results[0]
            
            cleaned_raw_value = row.get('cleaned_raw', {})
            if isinstance(cleaned_raw_value, str):
                try:
                    cleaned_raw = json.loads(cleaned_raw_value)
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse cleaned_raw JSON for college {college_id}")
                    cleaned_raw = {}
            elif isinstance(cleaned_raw_value, dict):
                cleaned_raw = cleaned_raw_value
            else:
                cleaned_raw = {}
            
            row['cleaned_raw'] = cleaned_raw
            
            college_data = CollegeData.from_db_row(row)
            college = College.from_college_data(college_data)
            
            logger.info(f"Successfully retrieved college data for ID {college_id}")
            return college
            
        except Exception as e:
            logger.error(f"Error retrieving college data for ID {college_id}: {e}")
            return None