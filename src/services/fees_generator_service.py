"""
Service layer for fees content generation operations.
"""
import os
from typing import Dict, List, Optional, Union

from langchain.schema import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from ..models.fees import FeesData
from ..models.generator import GeneratorConfig
from ..utils.exceptions import ContentGenerationError
from ..utils.logging_config import get_logger
from ..utils.prompts.fees import FeesPrompt

logger = get_logger(__name__)


class FeesGeneratorService:
    """Service for generating fees content."""

    def __init__(self, config: Optional[GeneratorConfig] = None):
        self.config = config or GeneratorConfig()
        
        if self.config.api_key:
            os.environ["GOOGLE_API_KEY"] = self.config.api_key
        
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=self.config.model,
                temperature=self.config.temperature
            )
            logger.info(f"Initialized ChatGoogleGenerativeAI for fees generation with model: {self.config.model}")
        except Exception as e:
            logger.error(f"Failed to initialize ChatGoogleGenerativeAI for fees: {e}")
            raise
        
        try:
            self.prompt_template = FeesPrompt().fees_prompt
            logger.info("Successfully loaded fees prompt template")
        except Exception as e:
            logger.error(f"Failed to load fees prompt template: {e}")
            raise

    def generate_fees_content(self, fees_data: Union[FeesData, List[FeesData]]) -> Union[str, Dict[str, str]]:
        """Generate fees content for single or multiple degrees."""
        if isinstance(fees_data, list):
            return self._generate_multiple_fees_content(fees_data)
        return self._generate_single_fees_content(fees_data)
    
    def _generate_multiple_fees_content(self, fees_data_list: List[FeesData]) -> Dict[str, str]:
        """Generate comprehensive overview for multiple degrees."""
        try:
            # Extract information from all degrees
            college_name = ""
            all_degree_names = []
            all_fee_info = []
            
            for fees_data in fees_data_list:
                if fees_data.degree_name:
                    all_degree_names.append(fees_data.degree_name)
                
                key_info = fees_data.extract_key_fee_info()
                all_fee_info.append(key_info)
                
                if not college_name and key_info.get("college_name") and key_info.get("college_name") != "the institution":
                    college_name = key_info["college_name"]
            
            if not all_degree_names:
                raise ContentGenerationError("No degree names found in fees data")
            
            # Combine fee ranges from all degrees
            fee_amounts = []
            facilities = {"mess": set(), "accommodation": set(), "scholarships": set()}
            
            for fee_info in all_fee_info:
                if fee_info.get("fee_range_min") != "contact institution":
                    fee_amounts.append(fee_info["fee_range_min"])
                if fee_info.get("fee_range_max") != "contact institution":
                    fee_amounts.append(fee_info["fee_range_max"])
                
                facilities["mess"].add(fee_info.get("mess_facility", "not specified"))
                facilities["accommodation"].add(fee_info.get("accommodation_facility", "not specified"))
                facilities["scholarships"].add(fee_info.get("scholarships", "merit-based scholarships"))
            
            # Determine overall fee range
            if fee_amounts:
                fee_range_min = min(fee_amounts, key=lambda x: self._extract_numeric_value(x))
                fee_range_max = max(fee_amounts, key=lambda x: self._extract_numeric_value(x))
            else:
                fee_range_min = fee_range_max = "contact institution"
            
            # Create comprehensive prompt variables
            prompt_vars = {
                "college_name": college_name or "this institution",
                "degree_name": ", ".join(all_degree_names),
                "fee_range_min": fee_range_min,
                "fee_range_max": fee_range_max,
                "mess_facility": "available" if "available" in facilities["mess"] else "not available",
                "accommodation_facility": "available" if "available" in facilities["accommodation"] else "not available",
                "scholarships": ", ".join([s for s in facilities["scholarships"] if s != "merit-based scholarships"]) or "merit-based scholarships"
            }
            
            logger.info(f"Generating comprehensive fees overview for {len(all_degree_names)} degrees at {college_name}")
            
            formatted_prompt = self.prompt_template.format(**prompt_vars)
            response = self.llm.invoke([HumanMessage(content=formatted_prompt)])
            
            if not response or not response.content:
                raise ContentGenerationError("Empty response from LLM")
            
            logger.info(f"Successfully generated comprehensive fees overview for {len(all_degree_names)} degrees")
            return {"overview": response.content}
            
        except Exception as e:
            logger.error(f"Error generating comprehensive fees content: {e}")
            raise ContentGenerationError(f"Comprehensive fees content generation failed: {e}")
    
    def _generate_single_fees_content(self, fees_data: FeesData) -> str:
        """Generate fees content for a single degree."""
        try:
            key_info = fees_data.extract_key_fee_info()
            
            prompt_vars = {
                "college_name": key_info.get("college_name") or "this institution",
                "degree_name": key_info.get("degree_name", "the program"),
                "fee_range_min": key_info.get("fee_range_min", "contact institution"),
                "fee_range_max": key_info.get("fee_range_max", "contact institution"),
                "mess_facility": key_info.get("mess_facility", "not specified"),
                "accommodation_facility": key_info.get("accommodation_facility", "not specified"),
                "scholarships": key_info.get("scholarships", "merit-based scholarships")
            }
            
            logger.info(f"Generating fees content for {prompt_vars['degree_name']} at {prompt_vars['college_name']}")
            
            formatted_prompt = self.prompt_template.format(**prompt_vars)
            
            response = self.llm.invoke([HumanMessage(content=formatted_prompt)])
            
            if not response or not response.content:
                raise ContentGenerationError("Empty response from LLM")
            
            logger.info(f"Successfully generated fees content for {prompt_vars['degree_name']}")
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating fees content: {e}")
            raise ContentGenerationError(f"Fees content generation failed: {e}")
    
    def _extract_numeric_value(self, amount_str: str) -> float:
        """Extract numeric value from amount string for comparison."""
        try:
            import re
            numbers = re.findall(r'\d+', amount_str.replace(',', ''))
            return float(numbers[0]) if numbers else 0
        except (ValueError, IndexError, AttributeError):
            return 0