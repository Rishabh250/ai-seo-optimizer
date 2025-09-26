"""
Service layer for overview short summary content generation operations.
"""
import os
from typing import Optional

from langchain.schema import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from ..models.college import College
from ..models.generator import GeneratorConfig
from ..utils.exceptions import ContentGenerationError
from ..utils.logging_config import get_logger
from ..utils.prompts.overview_short_summary import OverviewPrompt

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
            self.prompt_template = OverviewPrompt().overview_prompt
            logger.info("Successfully loaded overview short prompt template")
        except Exception as e:
            logger.error(f"Failed to load overview short prompt template: {e}")
            raise

    def generate_overview_short_content(self, college: College) -> str:
        """Generate overview short summary content for a college."""
        try:
            
            prompt_vars = {
                "college_name": college.college_name or "",
                "city": college.city or "",
                "state": college.state or "",
                "establishment_year": getattr(college, 'establishment_year', ''),
                "campus_area": getattr(college, 'campus_area', ''),
                "total_students": getattr(college, 'total_students', ''),
                "faculty_members": getattr(college, 'faculty_members', ''),
                "faculty_student_ratio": getattr(college, 'faculty_student_ratio', ''),
                "total_courses": getattr(college, 'total_courses', ''),
                "departments": getattr(college, 'departments', '')
            }
            
            logger.info(f"Generating overview short content for {prompt_vars['college_name']} in {prompt_vars['city']}, {prompt_vars['state']}")
            
            formatted_prompt = self.prompt_template.format(**prompt_vars)
            response = self.llm.invoke([HumanMessage(content=formatted_prompt)])
            
            if not response or not response.content:
                raise ContentGenerationError("Empty response from LLM")
            
            logger.info(f"Successfully generated overview short content for {prompt_vars['college_name']}")
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating overview short content: {e}")
            raise ContentGenerationError(f"Overview short content generation failed: {e}")
