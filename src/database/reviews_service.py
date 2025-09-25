"""
Service layer for reviews data operations.
"""
from typing import Optional

from ..models.reviews import ReviewsData
from ..utils.exceptions import CollegeNotFoundError
from ..utils.logging_config import get_logger
from .manager import get_db_manager

logger = get_logger(__name__)


class ReviewsService:
    """Service for managing reviews data operations."""

    def __init__(self):
        self.db = get_db_manager()

    def get_reviews_by_college_id(self, college_id: int, limit: int = 10) -> Optional[ReviewsData]:
        """Get reviews data for a college by ID."""
        try:
            query = """
                SELECT fgr.processed_output, fgr.raw_output, fs.college_name, fs.city, fs.state, fs.cleaned_raw
                FROM public.fmc_google_reviews fgr
                LEFT JOIN public.fmc_summary fs ON fgr.college_id = fs.college_id
                WHERE fgr.college_id = %(college_id)s 
                  AND fgr.processed_output IS NOT NULL 
                ORDER BY fgr.id DESC
                LIMIT %(limit)s
            """
            
            results = self.db.execute_raw_query(query, {"college_id": college_id, "limit": limit})
            
            if not results:
                logger.warning(f"No reviews data found for college ID {college_id}")
                raise CollegeNotFoundError(str(college_id), "ID")
            
            raw_output = results[0].get('processed_output', '{}')
            college_name = results[0].get('college_name', '')
            city = results[0].get('city', '')
            state = results[0].get('state', '')
            cleaned_raw = results[0].get('cleaned_raw', {})    
            
            try:
                reviews_data = ReviewsData.from_raw_output(college_id, raw_output, college_name, city, state, cleaned_raw)
                
                if not reviews_data.comments:
                    logger.warning(f"No high-rating reviews found for college ID {college_id}")
                    raise CollegeNotFoundError(str(college_id), "ID")
                
                logger.info(f"Successfully retrieved {len(reviews_data.comments)} high-rating reviews for college ID {college_id}")
                return reviews_data
                
            except Exception as e:
                logger.error(f"Error parsing reviews data for college ID {college_id}: {e}")
                raise CollegeNotFoundError(str(college_id), "ID")
            
        except CollegeNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving reviews data for college ID {college_id}: {e}")
            raise Exception(f"Failed to retrieve reviews data: {e}")
