"""
Enhanced fees content generator with comprehensive degree fees data integration and AI humanization retry.

This generator uses the comprehensive SQL query to fetch detailed fees information
and creates authentic institutional fees content focused on fee structures.
Includes intelligent AI humanization retry mechanism.
"""
import asyncio
import os
from typing import Dict, Optional

from langchain.schema import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from ..database.college_service import CollegeService
from ..database.fees_data_service import FeesDataService
from ..models.generator import GeneratorConfig
from ..services.ai_validation_service import AIValidationService
from ..utils.exceptions import (
    CollegeNotFoundError,
    ContentGenerationError,
    InvalidConfigurationError,
)
from ..utils.logging_config import get_logger
from ..utils.prompts.fees import FeesPrompt

logger = get_logger(__name__)

class FeesContentGenerator:
    """Enhanced fees content generator with comprehensive data integration."""

    def __init__(self, config: Optional[GeneratorConfig] = None):
        """Initialize the fees content generator."""
        self.config = config or GeneratorConfig()

        try:
            # Initialize services
            self.college_service = CollegeService()
            self.fees_data_service = FeesDataService()

            # Set up API key
            if self.config.api_key:
                os.environ["GOOGLE_API_KEY"] = self.config.api_key

            # Initialize AI model
            self.llm = ChatGoogleGenerativeAI(
                model=self.config.model,
                temperature=self.config.temperature
            )

            # Initialize prompt template
            self.prompt_template = FeesPrompt().fees_prompt

            logger.info("FeesContentGenerator initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize FeesContentGenerator: {e}")
            raise InvalidConfigurationError(f"Generator initialization failed: {e}")

    def generate_by_college_id(self, college_id: int) -> str:
        """
        Generate fees content for a college by ID.

        Args:
            college_id: The college ID to generate fees content for

        Returns:
            Generated fees content as a string

        Raises:
            CollegeNotFoundError: If college or fees data not found
            ContentGenerationError: If content generation fails
        """
        logger.info(f"Starting fees content generation for college ID: {college_id}")

        try:
            college = self.college_service.get_college_by_id(college_id)
            if not college:
                raise CollegeNotFoundError(str(college_id), "ID")

            fees_data = self.fees_data_service.get_fees_summary_for_prompt(college_id)
            if not fees_data:
                logger.warning(f"No fees data available for college {college_id}, using defaults")
                fees_data = self._get_default_fees_data()

            prompt_vars = self._prepare_prompt_variables(college, fees_data)

            formatted_prompt = self.prompt_template.format(**prompt_vars)

            logger.info(f"Generating fees content for {college.college_name}")

            response = self.llm.invoke([HumanMessage(content=formatted_prompt)])
            content = response.content.strip()

            if not content:
                raise ContentGenerationError(f"Empty content generated for college {college_id}")

            logger.info(f"Successfully generated fees content for college ID: {college_id}")
            return content

        except CollegeNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error generating fees content for college {college_id}: {e}")
            raise ContentGenerationError(f"Failed to generate fees content: {e}")

    def _prepare_prompt_variables(self, college, fees_data: dict) -> dict:
        """
        Prepare variables for the prompt template (without scholarship information).

        Args:
            college: College data object
            fees_data: Comprehensive fees data

        Returns:
            Dictionary of prompt variables
        """
        college_vars = college.to_prompt_vars()

        prompt_vars = {
            'college_name': college_vars.get('college_name', ''),
            'city': college_vars.get('city', ''),
            'state': college_vars.get('state', ''),
            'total_programs': fees_data.get('total_programs', '0'),
            'degree_levels': fees_data.get('degree_levels', 'various'),
            'fee_range': fees_data.get('fee_range', 'varies by program'),
            'accessibility_support': fees_data.get('accessibility_support', 'No'),
            'programs_list': fees_data.get('programs_list', 'various programs'),
            'specializations': fees_data.get('specializations', 'multiple specializations')
        }

        logger.debug(f"Prepared prompt variables: {list(prompt_vars.keys())}")
        return prompt_vars

    def _get_default_fees_data(self) -> dict:
        """
        Get default fees data when no specific data is available (without scholarships).

        Returns:
            Default fees data structure
        """
        return {
            'total_programs': '10+',
            'degree_levels': 'UG, PG',
            'fee_range': 'fees vary by program',
            'accessibility_support': 'Yes',
            'programs_list': 'engineering, management, science programs',
            'specializations': 'various specializations available'
        }

    async def generate_fees_with_retry(self, college_id: int, max_retries: int = 3, ai_validation_service: Optional[AIValidationService] = None) -> Dict[str, any]:
        """
        Generate fees content with AI humanization retry mechanism.

        Args:
            college_id: The college ID to generate fees content for
            max_retries: Maximum retry attempts for AI scores >90% (default: 3)
            ai_validation_service: AI validation service for scoring content

        Returns:
            Dictionary with content, AI score, and attempt information
        """
        best_content = None
        best_ai_score = None
        attempts = 0

        while attempts < max_retries:
            attempts += 1

            try:
                logger.info(f"🔄 (Attempt {attempts}/{max_retries}) Generating fees content for college {college_id}")

                content = self.generate_by_college_id(college_id)

                if not ai_validation_service:
                    return {
                        'content': content,
                        'ai_score': None,
                        'ai_percentage': None,
                        'attempts': attempts,
                        'success': True,
                        'humanized': False
                    }

                logger.info(f"🤖 Running AI validation for college {college_id} (Attempt {attempts}/{max_retries})")
                validation_result = await ai_validation_service.detect_ai_from_text(content)
                ai_score = validation_result.get('ai_detection_score', 0.0)
                ai_percentage = ai_score * 100

                logger.info(f"🤖 AI validation completed for college {college_id} (Attempt {attempts}/{max_retries}) - Score: {ai_score:.4f}")

                if best_content is None or (ai_score < best_ai_score if best_ai_score is not None else True):
                    best_content = content
                    best_ai_score = ai_score

                if ai_percentage <= 90.0:
                    logger.info(f"🎯 AI score {ai_percentage:.2f}% is acceptable for college {college_id}")
                    humanized = attempts > 1
                    return {
                        'content': content,
                        'ai_score': ai_score,
                        'ai_percentage': ai_percentage,
                        'attempts': attempts,
                        'success': True,
                        'humanized': humanized
                    }
                else:
                    logger.warning(f"⚠️ AI score {ai_percentage:.2f}% is too high for college {college_id}")
                    if attempts < max_retries:
                        logger.info(f"🔄 Retrying fees generation for college {college_id} (attempt {attempts + 1}/{max_retries})")
                        await asyncio.sleep(1)
                        continue

            except Exception as e:
                logger.error(f"❌ Error generating fees content for college {college_id} (Attempt {attempts}/{max_retries}): {e}")
                if attempts >= max_retries:
                    break
                await asyncio.sleep(1)
                continue

        if best_content:
            logger.warning(f"🎭 Using best available result for college {college_id} with AI score: {(best_ai_score * 100):.2f}%")
            return {
                'content': best_content,
                'ai_score': best_ai_score,
                'ai_percentage': best_ai_score * 100 if best_ai_score else None,
                'attempts': attempts,
                'success': True,
                'humanized': True
            }
        else:
            logger.error(f"❌ Failed to generate any content for college {college_id} after {attempts} attempts")
            return {
                'content': None,
                'ai_score': None,
                'ai_percentage': None,
                'attempts': attempts,
                'success': False,
                'humanized': False
            }

    def generate_fees_by_college_id(self, college_id: int, limit: int = 5) -> dict:
        """
        Legacy method for backward compatibility.

        Args:
            college_id: The college ID to generate fees content for
            limit: Not used in new implementation

        Returns:
            Dictionary with fees content for backward compatibility
        """
        content = self.generate_by_college_id(college_id)
        return {
            'overview': content,
            'fees_content': content,
            'college_id': college_id,
            'total_entries': 1
        }
