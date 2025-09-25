"""
Reviews content generator using service-oriented architecture.
"""
from typing import Dict, Optional

from ..database.reviews_service import ReviewsService
from ..models.generator import GeneratorConfig
from ..services.reviews_generator_service import ReviewsGeneratorService
from ..utils.exceptions import (
    CollegeNotFoundError,
    ContentGenerationError,
    InvalidConfigurationError,
    ReviewsNotFoundError,
)
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class ReviewsContentGenerator:
    """
    Main orchestrator for generating reviews content.
    
    This class coordinates between the reviews service and reviews generation service
    to produce high-quality reviews content.
    """

    def __init__(self, config: Optional[GeneratorConfig] = None):
        """Initialize the reviews content generator."""
        self.config = config or GeneratorConfig()
        
        try:
            self.reviews_service = ReviewsService()
            self.content_service = ReviewsGeneratorService(self.config)
            
            logger.info("ReviewsContentGenerator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ReviewsContentGenerator: {e}")
            raise InvalidConfigurationError(f"Reviews generator initialization failed: {e}")

    def generate_reviews_by_college_id(self, college_id: int, college_info: Optional[Dict] = None) -> str:
        """Generate reviews content for a college."""
        logger.info(f"Starting reviews content generation for college ID: {college_id}")
        
        try:
            reviews_data = self.reviews_service.get_reviews_by_college_id(college_id)

            if not reviews_data.comments:
                raise ReviewsNotFoundError(str(college_id), "ID")
            
            if not college_info:
                college_info = {
                    "college_name": reviews_data.college_name,
                    "city": reviews_data.city or "N/A",
                    "state": reviews_data.state or "N/A",
                    "establishment_year": reviews_data.cleaned_raw.get("Year_of_Establishment", "N/A"),
                    "campus_area": reviews_data.cleaned_raw.get("Campus_Area", "N/A"),
                    "reviews": reviews_data.comments or "N/A",
                }
            
            result = self.content_service.generate_reviews_content(reviews_data, college_info)
            
            logger.info(f"Successfully generated reviews content for college ID: {college_id}")
            return result
            
        except CollegeNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error generating reviews content for college ID {college_id}: {e}")
            raise ContentGenerationError(f"Failed to generate reviews content: {e}")
