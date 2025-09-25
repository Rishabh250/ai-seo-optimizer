"""
Simple college overview generator.
"""
import os
from typing import Optional

from langchain.schema import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from ..database.college_service import CollegeService
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
            
            if self.config.api_key:
                os.environ["GOOGLE_API_KEY"] = self.config.api_key
            
            self.llm = ChatGoogleGenerativeAI(
                model=self.config.model,
                temperature=self.config.temperature
            )
            
            # Load overview prompt
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
            
            formatted_prompt = self.prompt_template.format(
                college_name=college.college_name,
                city=college.city,
                state=college.state,
                establishment_year=getattr(college, 'establishment_year', ''),
                campus_area=getattr(college, 'campus_area', ''),
                total_students=getattr(college, 'total_students', ''),
                faculty_members=getattr(college, 'faculty_members', ''),
                faculty_student_ratio=getattr(college, 'faculty_student_ratio', ''),
                total_courses=getattr(college, 'total_courses', ''),
                departments=getattr(college, 'departments', '')
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

    def generate_by_name(self, college_name: str) -> str:
        """
        Generate college overview by college name.
        
        Args:
            college_name: The college name to search for and generate overview
            
        Returns:
            Generated overview content
            
        Raises:
            CollegeNotFoundError: If college is not found
            ContentGenerationError: If content generation fails
        """
        logger.info(f"Starting overview generation for college name: {college_name}")
        
        try:
            college = self.college_service.get_college_by_name(college_name)
            
            if not college:
                raise CollegeNotFoundError(college_name, "name")
            
            formatted_prompt = self.prompt_template.format(
                college_name=college.college_name,
                city=college.city,
                state=college.state,
                establishment_year=getattr(college, 'establishment_year', ''),
                campus_area=getattr(college, 'campus_area', ''),
                total_students=getattr(college, 'total_students', ''),
                faculty_members=getattr(college, 'faculty_members', ''),
                faculty_student_ratio=getattr(college, 'faculty_student_ratio', ''),
                total_courses=getattr(college, 'total_courses', ''),
                departments=getattr(college, 'departments', '')
            )
            
            response = self.llm.invoke([HumanMessage(content=formatted_prompt)])
            
            if not response or not response.content:
                raise ContentGenerationError("Empty response from LLM")
            
            logger.info(f"Successfully generated overview for college: {college_name}")
            return response.content
            
        except CollegeNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error generating overview for college '{college_name}': {e}")
            raise ContentGenerationError(f"Failed to generate overview: {e}")

    def validate_setup(self) -> bool:
        """
        Validate that the generator is properly set up and ready to use.
        
        Returns:
            True if setup is valid, False otherwise
        """
        try:    
            if not hasattr(self, 'college_service') or not self.college_service:
                logger.error("College service not initialized")
                return False
                
            if not hasattr(self, 'llm') or not self.llm:
                logger.error("LLM not initialized")
                return False
                
            if not hasattr(self, 'prompt_template') or not self.prompt_template:
                logger.error("Prompt template not initialized")
                return False
            
            logger.info("Generator setup validation successful")
            return True
            
        except Exception as e:
            logger.error(f"Error during setup validation: {e}")
            return False

    def get_statistics(self) -> dict:
        """
        Get statistics about available colleges.
        
        Returns:
            Dictionary containing statistics
        """
        try:
            stats = self.college_service.get_statistics()
            logger.info("Successfully retrieved college statistics")
            return stats
        except Exception as e:
            logger.error(f"Error retrieving statistics: {e}")
            return {}