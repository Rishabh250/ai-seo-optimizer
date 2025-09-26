"""
College overview short summary generator using service-oriented architecture.
"""
from typing import Optional

from ..database.college_service import CollegeService
from ..models.generator import GeneratorConfig
from ..services.overview_short_generator_service import OverviewShortGeneratorService
from ..utils.exceptions import (
    CollegeNotFoundError,
    ContentGenerationError,
    InvalidConfigurationError,
)
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class CollegeOverviewShortGenerator:
    """
    Main orchestrator for generating overview short summary content.
    
    This class coordinates between the college service and overview short generation service
    to produce high-quality short overview content.
    """

    def __init__(self, config: Optional[GeneratorConfig] = None):
        """Initialize the overview short summary generator."""
        self.config = config or GeneratorConfig()
        
        try:
            self.college_service = CollegeService()
            self.content_service = OverviewShortGeneratorService(self.config)
            
            logger.info("CollegeOverviewShortGenerator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize CollegeOverviewShortGenerator: {e}")
            raise InvalidConfigurationError(f"Overview short generator initialization failed: {e}")

    def generate_by_college_id(self, college_id: int) -> str:
        """Generate overview short summary content for a college by ID."""
        logger.info(f"Starting overview short generation for college ID: {college_id}")
        
        try:
            college = self.college_service.get_college_by_id(college_id)
            
            if not college:
                raise CollegeNotFoundError(str(college_id), "ID")
            
            result = self.content_service.generate_overview_short_content(college)
            
            logger.info(f"Successfully generated overview short content for college ID: {college_id}")
            return result
            
        except CollegeNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error generating overview short content for college ID {college_id}: {e}")
            raise ContentGenerationError(f"Failed to generate overview short content: {e}")
