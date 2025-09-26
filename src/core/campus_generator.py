"""
Campus content generator using service-oriented architecture.
"""
from typing import Optional

from ..database.campus_service import CampusService
from ..models.generator import GeneratorConfig
from ..services.campus_generator_service import CampusGeneratorService
from ..utils.exceptions import (
    CollegeNotFoundError,
    ContentGenerationError,
    InvalidConfigurationError,
)
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class CampusContentGenerator:
    """
    Main orchestrator for generating campus content.
    
    This class coordinates between the campus service and campus generation service
    to produce high-quality campus infrastructure content.
    """

    def __init__(self, config: Optional[GeneratorConfig] = None):
        """Initialize the campus content generator."""
        self.config = config or GeneratorConfig()
        
        try:
            self.campus_service = CampusService()
            self.content_service = CampusGeneratorService(self.config)
            
            logger.info("CampusContentGenerator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize CampusContentGenerator: {e}")
            raise InvalidConfigurationError(f"Campus generator initialization failed: {e}")

    def generate_campus_by_college_id(self, college_id: int) -> str:
        """Generate campus content for a college."""
        logger.info(f"Starting campus content generation for college ID: {college_id}")
        
        try:
            campus_data = self.campus_service.get_campus_by_college_id(college_id)
            result = self.content_service.generate_campus_content(campus_data)
            
            logger.info(f"Successfully generated campus content for college ID: {college_id}")
            return result
            
        except CollegeNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error generating campus content for college ID {college_id}: {e}")
            raise ContentGenerationError(f"Failed to generate campus content: {e}")
