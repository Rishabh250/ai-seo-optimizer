"""
Enhanced fees data service for fetching degree fees details.

This service uses the comprehensive SQL query to fetch detailed degree fees
information including fee structures, scholarships, and accessibility details.
"""
from typing import Any, Dict, List, Optional

from ..utils.exceptions import CollegeNotFoundError, DatabaseConnectionError
from ..utils.logging_config import get_logger
from .manager import DatabaseManager

logger = get_logger(__name__)


class FeesDataService:
    """Service for fetching comprehensive degree fees data."""

    def __init__(self):
        """Initialize the fees data service."""
        self.db_manager = DatabaseManager()

    def get_fees_data_by_college_id(self, college_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch comprehensive degree fees data for a college.

        Args:
            college_id: The college ID to fetch fees data for

        Returns:
            Dictionary containing comprehensive fees data or None if not found

        Raises:
            CollegeNotFoundError: If no fees data found for the college
            DatabaseConnectionError: If database operation fails
        """
        try:
            logger.info(f"Fetching comprehensive fees data for college ID: {college_id}")

            query = """
            SELECT
                college_id,
                jsonb_agg(json_build_object(
                  'college_id', college_id,
                  'degree_name', degree_name,
                  'degree_details', degree_details,
                  'specializations', specializations,
                  'fee_structure', raw_output->'fee_structure',
                  'scholarship_options', raw_output->'scholarship_options',
                  'pwd_accessibility', raw_output->'pwd_accessibility',
                  'reserved_category_fee_impact', raw_output->'reserved_category_fee_impact',
                  'extraction_metadata', raw_output->'extraction_metadata'
                )) as cleaned_json_object
              FROM fmc_degree_fees
              WHERE college_id = %s
              GROUP BY college_id
            """

            with self.db_manager.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (college_id,))
                    result = cursor.fetchone()

                    if not result:
                        logger.warning(f"No fees data found for college ID: {college_id}")
                        raise CollegeNotFoundError(str(college_id), "ID")

                    # Extract the data
                    college_id_result, fees_data = result

                    logger.info(f"Successfully retrieved fees data for college ID: {college_id}")

                    # Process the fees data
                    processed_data = self._process_fees_data(fees_data, college_id)
                    return processed_data

        except Exception as e:
            logger.error(f"Error fetching fees data for college {college_id}: {e}")
            if isinstance(e, CollegeNotFoundError):
                raise
            raise DatabaseConnectionError(f"Failed to fetch fees data: {e}")

    def _process_fees_data(self, fees_data: List[Dict], college_id: int) -> Dict[str, Any]:
        """
        Process raw fees data into a structured format for content generation.

        Args:
            fees_data: Raw fees data from database
            college_id: College ID for reference

        Returns:
            Processed fees data structure
        """
        if not fees_data:
            return {
                'college_id': college_id,
                'total_programs': 0,
                'degrees': [],
                'fee_summary': {},
                'scholarship_info': {},
                'accessibility_info': {}
            }

        # Initialize processed data structure
        processed = {
            'college_id': college_id,
            'total_programs': len(fees_data),
            'degrees': [],
            'fee_summary': {
                'min_fee': None,
                'max_fee': None,
                'average_fee': None,
                'fee_ranges': [],
                'payment_modes': set(),
                'scholarship_available': False
            },
            'scholarship_info': {
                'types': set(),
                'criteria': set(),
                'amounts': []
            },
            'accessibility_info': {
                'pwd_support': False,
                'reserved_category_benefits': False,
                'special_provisions': []
            },
            'degrees_by_level': {
                'UG': [],
                'PG': [],
                'PhD': [],
                'Diploma': [],
                'Certificate': []
            }
        }

        # Process each degree program
        for degree_data in fees_data:
            degree_info = self._extract_degree_info(degree_data)
            processed['degrees'].append(degree_info)

            # Update fee summary
            self._update_fee_summary(processed['fee_summary'], degree_data)

            # Update scholarship info
            self._update_scholarship_info(processed['scholarship_info'], degree_data)

            # Update accessibility info
            self._update_accessibility_info(processed['accessibility_info'], degree_data)

            # Categorize by degree level
            self._categorize_by_level(processed['degrees_by_level'], degree_info)

        # Calculate final statistics
        self._calculate_final_statistics(processed)

        logger.info(f"Processed {processed['total_programs']} degree programs for college {college_id}")
        return processed

    def _extract_degree_info(self, degree_data: Dict) -> Dict[str, Any]:
        """Extract and structure individual degree information."""
        return {
            'degree_name': degree_data.get('degree_name', ''),
            'degree_details': degree_data.get('degree_details', ''),
            'specializations': degree_data.get('specializations', []),
            'fee_structure': degree_data.get('fee_structure', {}),
            'scholarship_options': degree_data.get('scholarship_options', {}),
            'pwd_accessibility': degree_data.get('pwd_accessibility', {}),
            'reserved_category_fee_impact': degree_data.get('reserved_category_fee_impact', {}),
            'level': self._determine_degree_level(degree_data.get('degree_name', ''))
        }

    def _determine_degree_level(self, degree_name: str) -> str:
        """Determine the level of the degree (UG, PG, PhD, etc.)."""
        degree_name_lower = degree_name.lower()

        if any(term in degree_name_lower for term in ['b.tech', 'btech', 'bachelor', 'b.sc', 'bsc', 'b.com', 'bcom', 'b.a', 'ba', 'ug']):
            return 'UG'
        elif any(term in degree_name_lower for term in ['m.tech', 'mtech', 'master', 'm.sc', 'msc', 'm.com', 'mcom', 'm.a', 'ma', 'mba', 'pg']):
            return 'PG'
        elif any(term in degree_name_lower for term in ['phd', 'ph.d', 'doctorate']):
            return 'PhD'
        elif any(term in degree_name_lower for term in ['diploma', 'certificate']):
            return 'Diploma'
        else:
            return 'Other'

    def _update_fee_summary(self, fee_summary: Dict, degree_data: Dict) -> None:
        """Update fee summary with degree fee information."""
        fee_structure = degree_data.get('fee_structure', {})

        if isinstance(fee_structure, dict):
            # Extract fee amounts (look for common fee fields)
            fee_fields = ['total_fee', 'annual_fee', 'semester_fee', 'tuition_fee', 'course_fee']

            for field in fee_fields:
                if field in fee_structure:
                    fee_value = self._extract_numeric_fee(fee_structure[field])
                    if fee_value:
                        fee_summary['fee_ranges'].append(fee_value)

            # Check for scholarship availability
            scholarship_options = degree_data.get('scholarship_options', {})
            if scholarship_options and scholarship_options != {}:
                fee_summary['scholarship_available'] = True

    def _update_scholarship_info(self, scholarship_info: Dict, degree_data: Dict) -> None:
        """Update scholarship information."""
        scholarship_options = degree_data.get('scholarship_options', {})

        if isinstance(scholarship_options, dict) and scholarship_options:
            # Extract scholarship types
            if 'types' in scholarship_options:
                types = scholarship_options['types']
                if isinstance(types, list):
                    scholarship_info['types'].update(types)
                elif isinstance(types, str):
                    scholarship_info['types'].add(types)

            # Extract criteria
            if 'criteria' in scholarship_options:
                criteria = scholarship_options['criteria']
                if isinstance(criteria, list):
                    scholarship_info['criteria'].update(criteria)
                elif isinstance(criteria, str):
                    scholarship_info['criteria'].add(criteria)

    def _update_accessibility_info(self, accessibility_info: Dict, degree_data: Dict) -> None:
        """Update accessibility information."""
        pwd_accessibility = degree_data.get('pwd_accessibility', {})
        reserved_category = degree_data.get('reserved_category_fee_impact', {})

        if pwd_accessibility and pwd_accessibility != {}:
            accessibility_info['pwd_support'] = True

        if reserved_category and reserved_category != {}:
            accessibility_info['reserved_category_benefits'] = True

    def _categorize_by_level(self, degrees_by_level: Dict, degree_info: Dict) -> None:
        """Categorize degrees by their level."""
        level = degree_info.get('level', 'Other')
        if level in degrees_by_level:
            degrees_by_level[level].append(degree_info)
        else:
            degrees_by_level['Other'] = degrees_by_level.get('Other', [])
            degrees_by_level['Other'].append(degree_info)

    def _calculate_final_statistics(self, processed: Dict) -> None:
        """Calculate final fee statistics."""
        fee_ranges = processed['fee_summary']['fee_ranges']

        if fee_ranges:
            processed['fee_summary']['min_fee'] = min(fee_ranges)
            processed['fee_summary']['max_fee'] = max(fee_ranges)
            processed['fee_summary']['average_fee'] = sum(fee_ranges) / len(fee_ranges)

        # Convert sets to lists for JSON serialization
        processed['scholarship_info']['types'] = list(processed['scholarship_info']['types'])
        processed['scholarship_info']['criteria'] = list(processed['scholarship_info']['criteria'])

    def _extract_numeric_fee(self, fee_value: Any) -> Optional[float]:
        """Extract numeric fee value from various formats."""
        if isinstance(fee_value, (int, float)):
            return float(fee_value)

        if isinstance(fee_value, str):
            # Remove common currency symbols and text
            import re
            fee_str = re.sub(r'[^\d.]', '', fee_value)
            try:
                return float(fee_str) if fee_str else None
            except ValueError:
                return None

        return None

    def get_fees_summary_for_prompt(self, college_id: int) -> Dict[str, str]:
        """
        Get fees data formatted for prompt template usage.

        Args:
            college_id: College ID to fetch data for

        Returns:
            Dictionary with formatted fees data for prompt templates
        """
        try:
            fees_data = self.get_fees_data_by_college_id(college_id)

            if not fees_data:
                return {}

            formatted_data = {
                'total_programs': str(fees_data['total_programs']),
                'degree_levels': ', '.join([level for level, degrees in fees_data['degrees_by_level'].items() if degrees]),
                'fee_range': self._format_fee_range(fees_data['fee_summary']),
                'accessibility_support': 'Yes' if fees_data['accessibility_info']['pwd_support'] else 'No',
                'programs_list': self._format_programs_list(fees_data['degrees'][:5]),  # Limit to 5
                'specializations': self._format_specializations(fees_data['degrees'])
            }

            return formatted_data

        except Exception as e:
            logger.error(f"Error formatting fees data for prompt: {e}")
            return {}

    def _format_fee_range(self, fee_summary: Dict) -> str:
        """Format fee range for display."""
        min_fee = fee_summary.get('min_fee')
        max_fee = fee_summary.get('max_fee')

        if min_fee and max_fee:
            return f"INR {min_fee:,.0f} to INR {max_fee:,.0f}"
        elif min_fee:
            return f"Starting from INR {min_fee:,.0f}"
        else:
            return "Fees vary by program"

    def _format_programs_list(self, degrees: List[Dict]) -> str:
        """Format programs list for display."""
        program_names = [degree.get('degree_name', '') for degree in degrees if degree.get('degree_name')]
        return ', '.join(program_names[:5])  # Limit to 5 programs

    def _format_specializations(self, degrees: List[Dict]) -> str:
        """Format specializations for display."""
        all_specializations = []
        for degree in degrees:
            specializations = degree.get('specializations', [])
            if isinstance(specializations, list):
                all_specializations.extend(specializations)
            elif isinstance(specializations, str) and specializations:
                all_specializations.append(specializations)

        # Remove duplicates and limit
        unique_specializations = list(set(all_specializations))[:5]
        return ', '.join(unique_specializations) if unique_specializations else 'Various specializations available'