"""
Service layer for course content generation operations.
"""
import os
from typing import Optional

from langchain.schema import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from ..models.course import CourseData
from ..models.generator import GeneratorConfig
from ..utils.exceptions import ContentGenerationError
from ..utils.logging_config import get_logger
from ..utils.prompts.course import CoursePrompt

logger = get_logger(__name__)


class CourseGeneratorService:
    """Service for generating course content."""

    def __init__(self, config: Optional[GeneratorConfig] = None):
        self.config = config or GeneratorConfig()
        
        if self.config.api_key:
            os.environ["GOOGLE_API_KEY"] = self.config.api_key
        
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=self.config.model,
                temperature=self.config.temperature
            )
            logger.info(f"Initialized ChatGoogleGenerativeAI for course generation with model: {self.config.model}")
        except Exception as e:
            logger.error(f"Failed to initialize ChatGoogleGenerativeAI for course: {e}")
            raise
        
        try:
            self.prompt_template = CoursePrompt().course_prompt
            logger.info("Successfully loaded course prompt template")
        except Exception as e:
            logger.error(f"Failed to load course prompt template: {e}")
            raise

    def generate_course_content(self, course_data: CourseData) -> str:
        """Generate course content."""
        try:
            # Extract key information for prompt
            key_info = course_data.extract_key_course_info()
            
            prompt_vars = {
                "college_name": key_info.get("college_name", "the institution"),
                "city": key_info.get("city", ""),
                "state": key_info.get("state", ""),
                "establishment_year": key_info.get("establishment_year", ""),
                "campus_area": key_info.get("campus_area", ""),
                "courses": key_info.get("courses", "various courses")
            }
            
            logger.info(f"Generating course content for {prompt_vars['college_name']}")
            
            formatted_prompt = self.prompt_template.format(**prompt_vars)
            response = self.llm.invoke([HumanMessage(content=formatted_prompt)])
            
            if not response or not response.content:
                raise ContentGenerationError("Empty response from LLM")
            
            logger.info(f"Successfully generated course content for {prompt_vars['college_name']}")
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating course content: {e}")
            raise ContentGenerationError(f"Course content generation failed: {e}")
