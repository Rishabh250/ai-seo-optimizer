"""
Simple college overview generator.
"""
import os
from typing import Optional

from langchain.schema import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from src.database.course_service import CourseService
from src.services.course_generator_service import CourseGeneratorService

from ..database.college_service import CollegeService
from ..database.manager import DatabaseManager
from ..models.generator import GeneratorConfig
from ..utils.exceptions import (
    CollegeNotFoundError,
    ContentGenerationError,
    InvalidConfigurationError,
)
from ..utils.logging_config import get_logger
from ..utils.prompts.overview import OverviewPrompt

logger = get_logger(__name__)


class CollegeOverviewGenerator:
    """Simple college overview generator."""

    def __init__(self, config: Optional[GeneratorConfig] = None):
        """Initialize the college overview generator."""
        self.config = config or GeneratorConfig()
        
        try:
            self.college_service = CollegeService()
            self.course_service = CourseService()
            self.content_service = CourseGeneratorService(self.config)
            
            if self.config.api_key:
                os.environ["GOOGLE_API_KEY"] = self.config.api_key
            
            self.llm = ChatGoogleGenerativeAI(
                model=self.config.model,
                temperature=self.config.temperature
            )
            
            self.prompt_template = OverviewPrompt().overview_prompt
            
            logger.info("CollegeOverviewGenerator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize CollegeOverviewGenerator: {e}")
            raise InvalidConfigurationError(f"Generator initialization failed: {e}")

    def generate_by_college_id(self, college_id: int) -> str:
        """Generate college overview by college ID."""
        logger.info(f"Starting overview generation for college ID: {college_id}")
        
        try:
            college = self.college_service.get_college_by_id(college_id)
            
            if not college:
                raise CollegeNotFoundError(str(college_id), "ID")

            raw_data = self._prepare_raw_data(college.cleaned_raw)
            ranking_data = self._get_formatted_ranking_data(college_id)

            prompt_vars = college.to_prompt_vars()

            db_manager = DatabaseManager()
            clean_name_data = db_manager.get_clean_college_name(college_id)
            if clean_name_data:
                prompt_vars.update(clean_name_data)
            course_data = self.course_service.get_courses_by_college_id(college_id)

            formatted_prompt = self.prompt_template.format(
                **prompt_vars,
                raw_data=raw_data,
                ranking_data=ranking_data,
                courses=course_data.course_data
            )
            
            response = self.llm.invoke([HumanMessage(content=formatted_prompt)])
            
            if not response or not response.content:
                raise ContentGenerationError("Empty response from LLM")
            
            logger.info(f"Successfully generated overview for college ID: {college_id}")
            return response.content
            
        except CollegeNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error generating overview for college ID {college_id}: {e}")
            raise ContentGenerationError(f"Failed to generate overview: {e}")

    def _prepare_raw_data(self, cleaned_raw: dict) -> dict:
        """Prepare raw data by removing unnecessary fields."""
        raw_data = cleaned_raw.copy()
        
        if 'Data_Collection_Summary' in raw_data:
            data_summary = raw_data['Data_Collection_Summary'].copy()
            for key in ['Long_Summary', 'Short_Overview']:
                data_summary.pop(key, None)
            raw_data['Data_Collection_Summary'] = data_summary
        
        return raw_data

    def _get_formatted_ranking_data(self, college_id: int) -> str:
        """Get formatted ranking data for the college."""
        try:
            db_manager = DatabaseManager()
            ranking_data = db_manager.get_ranking_data_only(college_id)

            if not ranking_data:
                return "No ranking data available."

            ranking_groups = self._group_rankings_by_body(ranking_data)
            
            return self._format_ranking_groups(ranking_groups)

        except Exception as e:
            logger.warning(f"Failed to fetch ranking data for college {college_id}: {e}")
            return "Ranking data temporarily unavailable."

    def _group_rankings_by_body(self, ranking_data: list) -> dict:
        """Group ranking data by ranking body."""
        ranking_groups = {}
        
        for rank in ranking_data:
            body = rank['ranking_body']
            if body not in ranking_groups:
                ranking_groups[body] = []
            ranking_groups[body].append(rank)
        
        return ranking_groups

    def _format_ranking_groups(self, ranking_groups: dict) -> str:
        """Format ranking groups into a readable string."""
        formatted_rankings = [
            "College Rankings and Achievements:",
            "=" * 40
        ]

        for ranking_body, ranks in ranking_groups.items():
            formatted_rankings.append(f"\n{ranking_body}:")
            
            for rank in ranks:
                division = rank['division']
                rank_value = rank['rank']
                original_rank = rank['original_rank']

                display_rank = original_rank if '(' in original_rank else rank_value
                formatted_rankings.append(f"  • {division}: {display_rank}")

        return "\n".join(formatted_rankings)