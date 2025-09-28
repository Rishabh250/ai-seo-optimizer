"""
Service layer for course short content generation operations.
"""
import os
from typing import Optional

from langchain.schema import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from ..models.course import CourseData
from ..models.generator import GeneratorConfig
from ..utils.exceptions import ContentGenerationError
from ..utils.logging_config import get_logger
from ..utils.prompts.course_short import CourseShortPrompt

logger = get_logger(__name__)


class CourseShortGeneratorService:
    """Service for generating course short content."""

    def __init__(self, config: Optional[GeneratorConfig] = None):
        self.config = config or GeneratorConfig()

        if self.config.api_key:
            os.environ["GOOGLE_API_KEY"] = self.config.api_key

        try:
            self.llm = ChatGoogleGenerativeAI(
                model=self.config.model,
                temperature=self.config.temperature
            )
            logger.info(f"Initialized ChatGoogleGenerativeAI for course short generation with model: {self.config.model}")
        except Exception as e:
            logger.error(f"Failed to initialize ChatGoogleGenerativeAI for course short: {e}")
            raise

        try:
            self.prompt_template = CourseShortPrompt().course_short_prompt
            logger.info("Successfully loaded course short prompt template")
        except Exception as e:
            logger.error(f"Failed to load course short prompt template: {e}")
            raise

    def generate_course_short_content(self, course_data: CourseData) -> str:
        """Generate course short content."""
        try:
            key_info = course_data.extract_key_course_info()

            # Create a simplified course summary for short content
            courses_summary = self._create_short_course_summary(course_data)

            prompt_vars = {
                "college_name": key_info.get("college_name", "the institution"),
                "city": key_info.get("city", ""),
                "state": key_info.get("state", ""),
                "courses": courses_summary
            }

            logger.info(f"Generating course short content for {prompt_vars['college_name']} in {prompt_vars['city']}, {prompt_vars['state']}")

            formatted_prompt = self.prompt_template.format(**prompt_vars)
            response = self.llm.invoke([HumanMessage(content=formatted_prompt)])

            if not response or not response.content:
                raise ContentGenerationError("Empty response from LLM")

            logger.info(f"Successfully generated course short content for {prompt_vars['college_name']}")
            return response.content

        except Exception as e:
            logger.error(f"Error generating course short content: {e}")
            raise ContentGenerationError(f"Course short content generation failed: {e}")

    def _create_short_course_summary(self, course_data: CourseData) -> str:
        """Create a concise course summary for short content generation."""
        if not course_data.course_data:
            return "various undergraduate and postgraduate programs"

        # Group courses by level for summary
        levels = {"UG": [], "PG": [], "PhD": [], "Diploma": [], "Certificate": []}
        total_courses = len(course_data.course_data)
        domains = set()

        for course_name, course_details in course_data.course_data.items():
            if course_details.level:
                level = course_details.level.upper()
                if level in levels:
                    levels[level].append(course_name)
                else:
                    # Handle variations in level naming
                    if "UNDERGRADUATE" in level or "UG" in level or "BACHELOR" in level:
                        levels["UG"].append(course_name)
                    elif "POSTGRADUATE" in level or "PG" in level or "MASTER" in level:
                        levels["PG"].append(course_name)
                    elif "PHD" in level or "DOCTORAL" in level:
                        levels["PhD"].append(course_name)
                    elif "DIPLOMA" in level:
                        levels["Diploma"].append(course_name)
                    else:
                        levels["Certificate"].append(course_name)

            if course_details.domain:
                domains.add(course_details.domain)

        # Create summary parts
        summary_parts = []

        if levels["UG"]:
            summary_parts.append(f"{len(levels['UG'])} UG programs")
        if levels["PG"]:
            summary_parts.append(f"{len(levels['PG'])} PG programs")
        if levels["PhD"]:
            summary_parts.append(f"{len(levels['PhD'])} PhD programs")
        if levels["Diploma"]:
            summary_parts.append(f"{len(levels['Diploma'])} Diploma courses")

        course_summary = f"{total_courses} courses including " + ", ".join(summary_parts) if summary_parts else f"{total_courses} courses"

        if domains:
            domain_list = list(domains)[:3]  # Limit to first 3 domains for brevity
            domain_str = ", ".join(domain_list)
            if len(domains) > 3:
                domain_str += " and other areas"
            course_summary += f" across {domain_str}"

        return course_summary