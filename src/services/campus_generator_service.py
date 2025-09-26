"""
Service layer for campus content generation operations.
"""
import os
from typing import Optional

from langchain.schema import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from ..models.campus import CampusData
from ..models.generator import GeneratorConfig
from ..utils.exceptions import ContentGenerationError
from ..utils.logging_config import get_logger
from ..utils.prompts.campus import CampusPrompt

logger = get_logger(__name__)


class CampusGeneratorService:
    """Service for generating campus content."""

    def __init__(self, config: Optional[GeneratorConfig] = None):
        self.config = config or GeneratorConfig()
        
        if self.config.api_key:
            os.environ["GOOGLE_API_KEY"] = self.config.api_key
        
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=self.config.model,
                temperature=self.config.temperature
            )
            logger.info(f"Initialized ChatGoogleGenerativeAI for campus generation with model: {self.config.model}")
        except Exception as e:
            logger.error(f"Failed to initialize ChatGoogleGenerativeAI for campus: {e}")
            raise
        
        try:
            self.prompt_template = CampusPrompt().campus_prompt
            logger.info("Successfully loaded campus prompt template")
        except Exception as e:
            logger.error(f"Failed to load campus prompt template: {e}")
            raise

    def generate_campus_content(self, campus_data: CampusData) -> str:
        """Generate campus content for a college."""
        try:
            key_info = campus_data.extract_key_campus_info()
            
            # Extract college name and location for prompt
            college_name = key_info.get("college_name", "the institution")
            location_parts = key_info.get("location", "").split(", ")
            city = location_parts[0] if location_parts else "the city"
            state = location_parts[1] if len(location_parts) > 1 else "the state"
            
            prompt_vars = {
                "college_name": college_name,
                "city": city,
                "state": state
            }
            
            logger.info(f"Generating campus content for {college_name} in {city}, {state}")
            
            formatted_prompt = self.prompt_template.format(**prompt_vars)
            response = self.llm.invoke([HumanMessage(content=formatted_prompt)])
            
            if not response or not response.content:
                raise ContentGenerationError("Empty response from LLM")
            
            logger.info(f"Successfully generated campus content for {college_name}")
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating campus content: {e}")
            raise ContentGenerationError(f"Campus content generation failed: {e}")
