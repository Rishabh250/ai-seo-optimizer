"""
Course content generator using service-oriented architecture.
"""
from typing import Optional

from ..database.course_service import CourseService
from ..models.generator import GeneratorConfig
from ..services.course_generator_service import CourseGeneratorService
from ..utils.exceptions import (
    CollegeNotFoundError,
    ContentGenerationError,
    InvalidConfigurationError,
)
from ..utils.logging_config import get_logger

logger = get_logger(__name__)

class CourseContentGenerator:
    """
    Main orchestrator for generating course content.
    
    This class coordinates between the course service and course generation service
    to produce high-quality course content.
    """

    def __init__(self, config: Optional[GeneratorConfig] = None):
        """Initialize the course content generator."""
        self.config = config or GeneratorConfig()
        
        try:
            self.course_service = CourseService()
            self.content_service = CourseGeneratorService(self.config)
            
            logger.info("CourseContentGenerator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize CourseContentGenerator: {e}")
            raise InvalidConfigurationError(f"Course generator initialization failed: {e}")

    async def generate_courses_by_college_id(self, college_id: int) -> str:
        """Generate course content for a college with AI validation."""
        logger.info(f"Starting course content generation for college ID: {college_id}")
        
        try:
            course_data = self.course_service.get_courses_by_college_id(college_id)
            result = self.content_service.generate_course_content(course_data)
            
            logger.info(f"Successfully generated course content for college ID: {college_id}")

            
            return result
            
        except CollegeNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error generating course content for college ID {college_id}: {e}")
            raise ContentGenerationError(f"Failed to generate course content: {e}")
