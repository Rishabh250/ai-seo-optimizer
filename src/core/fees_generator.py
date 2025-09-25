"""
Fees content generator using service-oriented architecture.
"""
from typing import Dict, List, Optional

from ..database.fees_service import FeesService
from ..models.generator import GeneratorConfig
from ..services.fees_generator_service import FeesGeneratorService
from ..utils.exceptions import (
    CollegeNotFoundError,
    ContentGenerationError,
    InvalidConfigurationError,
)
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class FeesContentGenerator:
    """
    Main orchestrator for generating fees content.
    
    This class coordinates between the fees service and fees generation service
    to produce high-quality fees content.
    """

    def __init__(self, config: Optional[GeneratorConfig] = None):
        """Initialize the fees content generator."""
        self.config = config or GeneratorConfig()
        
        try:
            self.fees_service = FeesService()
            self.content_service = FeesGeneratorService(self.config)
            
            logger.info("FeesContentGenerator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize FeesContentGenerator: {e}")
            raise InvalidConfigurationError(f"Fees generator initialization failed: {e}")

    def generate_fees_by_college_id(self, college_id: int, limit: int = 5) -> Dict[str, str]:
        """Generate fees content for all degrees at a college."""
        logger.info(f"Starting fees content generation for college ID: {college_id}")
        
        try:
            fees_data_list = self.fees_service.get_fees_by_college_id(college_id, limit)
            results = self.content_service.generate_fees_content(fees_data_list)
            
            logger.info(f"Successfully generated fees content for {len(results)} degrees at college ID: {college_id}")
            return results
            
        except CollegeNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error generating fees content for college ID {college_id}: {e}")
            raise ContentGenerationError(f"Failed to generate fees content: {e}")
