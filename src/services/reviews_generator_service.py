"""
Service layer for reviews content generation operations.
"""
import os
from typing import Optional

from langchain.schema import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from ..models.generator import GeneratorConfig
from ..models.reviews import ReviewsData
from ..utils.exceptions import ContentGenerationError
from ..utils.logging_config import get_logger
from ..utils.prompts.reviews import ReviewsPrompt

logger = get_logger(__name__)


class ReviewsGeneratorService:
    """Service for generating reviews content."""

    def __init__(self, config: Optional[GeneratorConfig] = None):
        self.config = config or GeneratorConfig()
        
        if self.config.api_key:
            os.environ["GOOGLE_API_KEY"] = self.config.api_key
        
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=self.config.model,
                temperature=self.config.temperature
            )
            logger.info(f"Initialized ChatGoogleGenerativeAI for reviews generation with model: {self.config.model}")
        except Exception as e:
            logger.error(f"Failed to initialize ChatGoogleGenerativeAI for reviews: {e}")
            raise
        
        try:
            self.prompt_template = ReviewsPrompt().reviews_prompt
            logger.info("Successfully loaded reviews prompt template")
        except Exception as e:
            logger.error(f"Failed to load reviews prompt template: {e}")
            raise

    def generate_reviews_content(self, reviews_data: ReviewsData, college_info: dict) -> str:
        """Generate reviews content for a college."""
        try:
            review_info = reviews_data.extract_key_review_info()
            
            reviews_text = ""
            if review_info.get("sample_comments"):
                reviews_text = " | ".join(review_info["sample_comments"][:3])
            else:
                reviews_text = "Students appreciate the academic quality and campus environment."
            
            prompt_vars = {
                "college_name": college_info.get("college_name", "the institution"),
                "city": college_info.get("city", ""),
                "state": college_info.get("state", ""),
                "establishment_year": college_info.get("establishment_year", ""),
                "campus_area": college_info.get("campus_area", ""),
                "reviews": reviews_text
            }
            
            prompt_vars = {k: v for k, v in prompt_vars.items() if v}
            
            logger.info(f"Generating reviews content for {prompt_vars.get('college_name', 'college')}")
            
            formatted_prompt = self.prompt_template.format(**prompt_vars)
            
            response = self.llm.invoke([HumanMessage(content=formatted_prompt)])
            
            if not response or not response.content:
                raise ContentGenerationError("Empty response from LLM")
            
            logger.info(f"Successfully generated reviews content for {prompt_vars.get('college_name', 'college')}")
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating reviews content: {e}")
            raise ContentGenerationError(f"Reviews content generation failed: {e}")
