"""
College overview short summary generator using service-oriented architecture.
"""
from typing import Optional

from ..database.college_service import CollegeService
from ..database.course_service import CourseService
from ..database.manager import DatabaseManager
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
            self.course_service = CourseService()
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

            raw_data = self._prepare_raw_data(college.cleaned_raw)
            ranking_data = self.content_service._get_formatted_ranking_data(college_id)

            # Handle course data with error fallback
            try:
                courses = self.course_service.get_courses_by_college_id(college_id).course_data
            except Exception as course_error:
                logger.warning(f"Failed to retrieve course data for college {college_id}: {course_error}")
                courses = {}

            prompt_vars = college.to_prompt_vars()

            db_manager = DatabaseManager()
            clean_name_data = db_manager.get_clean_college_name(college_id)
            if clean_name_data:
                prompt_vars.update(clean_name_data)
            
            result = self.content_service.generate_overview_short_content(college, prompt_vars, raw_data, ranking_data, courses)
            
            logger.info(f"Successfully generated overview short content for college ID: {college_id}")
            return result
            
        except CollegeNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error generating overview short content for college ID {college_id}: {e}")
            raise ContentGenerationError(f"Failed to generate overview short content: {e}")

    def _prepare_raw_data(self, cleaned_raw: dict) -> dict:
        """Prepare raw data by removing unnecessary fields."""
        raw_data = cleaned_raw.copy()
        
        if 'Data_Collection_Summary' in raw_data:
            data_summary = raw_data['Data_Collection_Summary'].copy()
            for key in ['Long_Summary', 'Short_Overview']:
                data_summary.pop(key, None)
            raw_data['Data_Collection_Summary'] = data_summary
        
        return raw_data
