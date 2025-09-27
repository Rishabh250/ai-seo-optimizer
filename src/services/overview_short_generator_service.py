"""
Service layer for overview short summary content generation operations.
"""
import os
from typing import Optional

from langchain.schema import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from ..database.manager import DatabaseManager
from ..models.college import College
from ..models.generator import GeneratorConfig
from ..utils.exceptions import ContentGenerationError
from ..utils.logging_config import get_logger
from ..utils.prompts.overview_short_summary import OverviewShortSummaryPrompt

logger = get_logger(__name__)


class OverviewShortGeneratorService:
    """Service for generating overview short summary content."""

    def __init__(self, config: Optional[GeneratorConfig] = None):
        self.config = config or GeneratorConfig()
        
        if self.config.api_key:
            os.environ["GOOGLE_API_KEY"] = self.config.api_key
        
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=self.config.model,
                temperature=self.config.temperature
            )
            logger.info(f"Initialized ChatGoogleGenerativeAI for overview short generation with model: {self.config.model}")
        except Exception as e:
            logger.error(f"Failed to initialize ChatGoogleGenerativeAI for overview short: {e}")
            raise
        
        try:
            self.prompt_template = OverviewShortSummaryPrompt().overview_short_summary_prompt
            logger.info("Successfully loaded overview short prompt template")
        except Exception as e:
            logger.error(f"Failed to load overview short prompt template: {e}")
            raise

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

    def generate_overview_short_content(self, college: College, prompt_vars: dict, raw_data: dict, ranking_data: str, courses: dict) -> str:
        """Generate overview short summary content for a college."""
        try:
            
            formatted_prompt_vars = {
                "college_name": prompt_vars.get('college_name', ''),
                "city": prompt_vars.get('city', ''),
                "state": prompt_vars.get('state', ''),
                "establishment_year": prompt_vars.get('establishment_year', ''),
                "campus_area": prompt_vars.get('campus_area', ''),
                "total_students": prompt_vars.get('total_students', ''),
                "faculty_members": prompt_vars.get('faculty_members', ''),
                "faculty_student_ratio": prompt_vars.get('faculty_student_ratio', ''),
                "total_courses": prompt_vars.get('total_courses', ''),
                "departments": prompt_vars.get('departments', ''),
                "raw_data": raw_data,
                "ranking_data": ranking_data,
                "courses": courses
            }
            
            logger.info(f"Generating overview short content for {formatted_prompt_vars['college_name']} in {formatted_prompt_vars['city']}, {formatted_prompt_vars['state']}")
            
            formatted_prompt = self.prompt_template.format(**formatted_prompt_vars)
            response = self.llm.invoke([HumanMessage(content=formatted_prompt)])
            
            if not response or not response.content:
                raise ContentGenerationError("Empty response from LLM")
            
            logger.info(f"Successfully generated overview short content for {formatted_prompt_vars['college_name']}")
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating overview short content: {e}")
            raise ContentGenerationError(f"Overview short content generation failed: {e}")
