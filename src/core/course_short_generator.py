"""
Course short content generator using service-oriented architecture.
"""
from typing import Optional

from ..database.course_service import CourseService
from ..models.generator import GeneratorConfig
from ..services.course_short_generator_service import CourseShortGeneratorService
from ..utils.exceptions import (
    CollegeNotFoundError,
    ContentGenerationError,
    InvalidConfigurationError,
)
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class CourseShortContentGenerator:
    """
    Main orchestrator for generating course short content.

    This class coordinates between the course service and course short generation service
    to produce high-quality short course content.
    """

    def __init__(self, config: Optional[GeneratorConfig] = None):
        """Initialize the course short content generator."""
        self.config = config or GeneratorConfig()

        try:
            self.course_service = CourseService()
            self.content_service = CourseShortGeneratorService(self.config)

            logger.info("CourseShortContentGenerator initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize CourseShortContentGenerator: {e}")
            raise InvalidConfigurationError(f"Course short generator initialization failed: {e}")

    async def generate_course_short_by_college_id(self, college_id: int) -> str:
        """Generate course short content for a college."""
        logger.info(f"Starting course short content generation for college ID: {college_id}")

        try:
            course_data = self.course_service.get_courses_by_college_id(college_id)

            if not course_data:
                raise CollegeNotFoundError(str(college_id), "course data")

            result = self.content_service.generate_course_short_content(course_data)

            logger.info(f"Successfully generated course short content for college ID: {college_id}")
            return result

        except CollegeNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error generating course short content for college ID {college_id}: {e}")
            raise ContentGenerationError(f"Failed to generate course short content: {e}")

    def generate_course_short_by_college_id_sync(self, college_id: int) -> str:
        """Synchronous version of course short content generation for a college."""
        logger.info(f"Starting synchronous course short content generation for college ID: {college_id}")

        try:
            course_data = self.course_service.get_courses_by_college_id(college_id)

            if not course_data:
                raise CollegeNotFoundError(str(college_id), "course data")

            result = self.content_service.generate_course_short_content(course_data)

            logger.info(f"Successfully generated course short content for college ID: {college_id}")
            return result

        except CollegeNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error generating course short content for college ID {college_id}: {e}")
            raise ContentGenerationError(f"Failed to generate course short content: {e}")