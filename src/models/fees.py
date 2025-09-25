"""
Data models for fees information.
"""
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class FeeComponent:
    """Individual fee component structure."""
    amount: Optional[str] = None
    mandatory: Optional[bool] = None
    data_source: Optional[str] = None
    important_note: List[str] = field(default_factory=list)
    one_time_payment: Optional[bool] = None
    payment_due_period: Optional[str] = None


@dataclass
class TuitionFee:
    """Tuition fee structure."""
    data_source: Optional[str] = None
    important_note: List[str] = field(default_factory=list)
    payment_due_period: Optional[str] = None
    specialization_fee: Dict[str, str] = field(default_factory=dict)


@dataclass
class MessFee:
    """Mess fee structure."""
    general: Optional[str] = None
    meal_plan: List[str] = field(default_factory=list)
    data_source: Optional[str] = None
    mess_facility: Optional[bool] = None
    important_note: List[str] = field(default_factory=list)
    payment_due_period: Optional[str] = None
    available_food_options: List[str] = field(default_factory=list)


@dataclass
class AccommodationChoice:
    """Accommodation choice details."""
    amount: Optional[str] = None
    amenities: List[str] = field(default_factory=list)
    maintenance_fee: Optional[str] = None
    security_deposit: Optional[str] = None
    electricity_charges: Optional[str] = None
    one_time_fee_components: List[str] = field(default_factory=list)


@dataclass
class AccommodationFee:
    """Accommodation fee structure."""
    data_source: Optional[str] = None
    important_note: List[str] = field(default_factory=list)
    minimum_amount: Optional[str] = None
    girls_only_stay: Optional[bool] = None
    payment_due_period: Optional[str] = None
    accommodation_facility: Optional[bool] = None
    accommodation_choice: Dict[str, AccommodationChoice] = field(default_factory=dict)


@dataclass
class FeeStructure:
    """Complete fee structure."""
    tuition_fee: Optional[TuitionFee] = None
    mess_fee: Optional[MessFee] = None
    library_fee: Optional[FeeComponent] = None
    caution_deposit: Optional[FeeComponent] = None
    examination_fee: Optional[FeeComponent] = None
    registration_fee: Optional[FeeComponent] = None
    accommodation_fee: Optional[AccommodationFee] = None
    all_fee_components: List[str] = field(default_factory=list)


@dataclass
class CategoryFeeImpact:
    """Fee impact for reserved categories."""
    amount: Optional[str] = None
    important_note: Optional[str] = None
    tuition_fees_per: Optional[str] = None


@dataclass
class ScholarshipOption:
    """Scholarship information."""
    name: Optional[str] = None
    data_source: Optional[str] = None
    eligibility: Optional[str] = None
    benefit_type: Optional[str] = None
    benefit_amount: Optional[str] = None
    benefit_percentage: Optional[str] = None
    important_note_terms: Optional[str] = None


@dataclass
class PWDAccessibility:
    """PWD accessibility information."""
    applicable: Optional[bool] = None
    data_source: Optional[str] = None
    fee_relaxation: Dict[str, str] = field(default_factory=dict)
    academic_support: List[str] = field(default_factory=list)
    supported_disabilities: List[str] = field(default_factory=list)


@dataclass
class DaySchoolingOption:
    """Day schooling option details."""
    available: Optional[bool] = None
    conditions: Optional[str] = None
    data_source: Optional[str] = None
    additional_requirements: Optional[str] = None


@dataclass
class ExtractionMetadata:
    """Metadata about the data extraction."""
    course: Optional[str] = None
    college: Optional[str] = None
    data_completeness: Optional[str] = None
    data_sources_used: Dict[str, List[str]] = field(default_factory=dict)
    academic_year_data: Optional[str] = None
    data_recency_check: Dict[str, Any] = field(default_factory=dict)
    extraction_approach: Optional[str] = None


@dataclass
class FeesData:
    """Complete fees data structure."""
    degree_name: Optional[str] = None
    fee_structure: Optional[FeeStructure] = None
    pwd_accessibility: Optional[PWDAccessibility] = None
    extraction_metadata: Optional[ExtractionMetadata] = None
    scholarship_options: List[ScholarshipOption] = field(default_factory=list)
    day_schooling_option: Optional[DaySchoolingOption] = None
    reserved_category_fee_impact: Dict[str, CategoryFeeImpact] = field(default_factory=dict)

    @classmethod
    def from_raw_output(cls, degree_name: str, raw_output: str) -> "FeesData":
        """Create FeesData from raw JSON output."""
        try:
            if isinstance(raw_output, str):
                data = json.loads(raw_output)
            else:
                data = raw_output
        except json.JSONDecodeError:
            return cls(degree_name=degree_name)

        return cls(
            degree_name=degree_name,
            fee_structure=cls._parse_fee_structure(data.get("fee_structure", {})),
            pwd_accessibility=cls._parse_pwd_accessibility(data.get("pwd_accessibility", {})),
            extraction_metadata=cls._parse_extraction_metadata(data.get("extraction_metadata", {})),
            scholarship_options=cls._parse_scholarship_options(data.get("scholarship_options", [])),
            day_schooling_option=cls._parse_day_schooling_option(data.get("day_schooling_option", {})),
            reserved_category_fee_impact=cls._parse_reserved_category_fee_impact(
                data.get("reserved_category_fee_impact", {})
            )
        )

    @staticmethod
    def _parse_fee_structure(data: Dict[str, Any]) -> Optional[FeeStructure]:
        """Parse fee structure from raw data."""
        if not data:
            return None

        return FeeStructure(
            tuition_fee=FeesData._parse_tuition_fee(data.get("tuition_fee", {})),
            mess_fee=FeesData._parse_mess_fee(data.get("mess_fee", {})),
            library_fee=FeesData._parse_fee_component(data.get("library_fee", {})),
            caution_deposit=FeesData._parse_fee_component(data.get("caution_deposit", {})),
            examination_fee=FeesData._parse_fee_component(data.get("examination_fee", {})),
            registration_fee=FeesData._parse_fee_component(data.get("regitration_fee", {})),  # Note: typo in original
            accommodation_fee=FeesData._parse_accommodation_fee(data.get("accomodation_fee", {})),  # Note: typo in original
            all_fee_components=data.get("all_fee_components", [])
        )

    @staticmethod
    def _parse_tuition_fee(data: Dict[str, Any]) -> Optional[TuitionFee]:
        """Parse tuition fee from raw data."""
        if not data:
            return None

        return TuitionFee(
            data_source=data.get("data_source"),
            important_note=data.get("important_note", []),
            payment_due_period=data.get("payment_due_period"),
            specialization_fee=data.get("specialization_fee", {})
        )

    @staticmethod
    def _parse_mess_fee(data: Dict[str, Any]) -> Optional[MessFee]:
        """Parse mess fee from raw data."""
        if not data:
            return None

        return MessFee(
            general=data.get("general"),
            meal_plan=data.get("meal_plan", []),
            data_source=data.get("data_source"),
            mess_facility=data.get("mess_facility"),
            important_note=data.get("important_note", []),
            payment_due_period=data.get("payment_due_period"),
            available_food_options=data.get("available_food_options", [])
        )

    @staticmethod
    def _parse_fee_component(data: Dict[str, Any]) -> Optional[FeeComponent]:
        """Parse fee component from raw data."""
        if not data:
            return None

        return FeeComponent(
            amount=data.get("amount"),
            mandatory=data.get("mandatory"),
            data_source=data.get("data_source"),
            important_note=data.get("important_note", []),
            one_time_payment=data.get("one_time_payment"),
            payment_due_period=data.get("payment_due_period")
        )

    @staticmethod
    def _parse_accommodation_fee(data: Dict[str, Any]) -> Optional[AccommodationFee]:
        """Parse accommodation fee from raw data."""
        if not data:
            return None

        accommodation_choices = {}
        for key, value in data.get("accomodotion_choice", {}).items():  # Note: typo in original
            if isinstance(value, dict):
                accommodation_choices[key] = AccommodationChoice(
                    amount=value.get("amount"),
                    amenities=value.get("amenities", []),
                    maintenance_fee=value.get("maintenance_fee"),
                    security_deposit=value.get("security_deposit"),
                    electricity_charges=value.get("electricity_charges"),
                    one_time_fee_components=value.get("one_time_fee_componenets", [])  # Note: typo in original
                )

        return AccommodationFee(
            data_source=data.get("data_source"),
            important_note=data.get("important_note", []),
            minimum_amount=data.get("minimum_amount"),
            girls_only_stay=data.get("girls_only_stay"),
            payment_due_period=data.get("payment_due_period"),
            accommodation_facility=data.get("accomation_facility"),  # Note: typo in original
            accommodation_choice=accommodation_choices
        )

    @staticmethod
    def _parse_pwd_accessibility(data: Dict[str, Any]) -> Optional[PWDAccessibility]:
        """Parse PWD accessibility from raw data."""
        if not data:
            return None

        return PWDAccessibility(
            applicable=data.get("applicable"),
            data_source=data.get("data_source"),
            fee_relaxation=data.get("fee_relaxation", {}),
            academic_support=data.get("academic_support", []),
            supported_disabilities=data.get("supported_disabilities", [])
        )

    @staticmethod
    def _parse_extraction_metadata(data: Dict[str, Any]) -> Optional[ExtractionMetadata]:
        """Parse extraction metadata from raw data."""
        if not data:
            return None

        return ExtractionMetadata(
            course=data.get("course"),
            college=data.get("college"),
            data_completeness=data.get("data_completeness"),
            data_sources_used=data.get("data_sources_used", {}),
            academic_year_data=data.get("academic_year_data"),
            data_recency_check=data.get("data_recency_check", {}),
            extraction_approach=data.get("extraction_approach")
        )

    @staticmethod
    def _parse_scholarship_options(data: List[Dict[str, Any]]) -> List[ScholarshipOption]:
        """Parse scholarship options from raw data."""
        scholarships = []
        for item in data:
            if isinstance(item, dict):
                scholarships.append(ScholarshipOption(
                    name=item.get("name"),
                    data_source=item.get("data_source"),
                    eligibility=item.get("eligibility"),
                    benefit_type=item.get("benefit_type"),
                    benefit_amount=item.get("benefit_amount"),
                    benefit_percentage=item.get("benefit_percentage"),
                    important_note_terms=item.get("important_note/terms")
                ))
        return scholarships

    @staticmethod
    def _parse_day_schooling_option(data: Dict[str, Any]) -> Optional[DaySchoolingOption]:
        """Parse day schooling option from raw data."""
        if not data:
            return None

        return DaySchoolingOption(
            available=data.get("available"),
            conditions=data.get("conditions"),
            data_source=data.get("data_source"),
            additional_requirements=data.get("additional_requirements")
        )

    @staticmethod
    def _parse_reserved_category_fee_impact(data: Dict[str, Any]) -> Dict[str, CategoryFeeImpact]:
        """Parse reserved category fee impact from raw data."""
        category_impacts = {}
        for category, impact_data in data.items():
            if isinstance(impact_data, dict):
                category_impacts[category] = CategoryFeeImpact(
                    amount=impact_data.get("amount"),
                    important_note=impact_data.get("important_note"),
                    tuition_fees_per=impact_data.get("tution_fees_per")  # Note: typo in original
                )
        return category_impacts

    def extract_key_fee_info(self) -> Dict[str, str]:
        """Extract key fee information for content generation."""
        info = {}
        
        info["degree_name"] = self.degree_name or "the program"
        
        if self.extraction_metadata and self.extraction_metadata.college:
            info["college_name"] = self.extraction_metadata.college
        else:
            return {}
        
        fee_amounts = []
        
        if self.fee_structure:
            if self.fee_structure.tuition_fee and self.fee_structure.tuition_fee.specialization_fee:
                for spec, amount in self.fee_structure.tuition_fee.specialization_fee.items():
                    if amount and amount != "NA":
                        fee_amounts.append(amount)
            
            fee_components = [
                self.fee_structure.library_fee,
                self.fee_structure.caution_deposit,
                self.fee_structure.examination_fee,
                self.fee_structure.registration_fee
            ]
            
            for component in fee_components:
                if component and component.amount and component.amount != "NA":
                    fee_amounts.append(component.amount)
        
        if fee_amounts:
            info["fee_range_min"] = min(fee_amounts, key=lambda x: self._extract_numeric_value(x))
            info["fee_range_max"] = max(fee_amounts, key=lambda x: self._extract_numeric_value(x))
        else:
            info["fee_range_min"] = "contact institution"
            info["fee_range_max"] = "contact institution"
        
        info["mess_facility"] = "available" if (self.fee_structure and 
                                              self.fee_structure.mess_fee and 
                                              self.fee_structure.mess_fee.mess_facility) else "not available"
        
        info["accommodation_facility"] = "available" if (self.fee_structure and 
                                                       self.fee_structure.accommodation_fee and 
                                                       self.fee_structure.accommodation_fee.accommodation_facility) else "not available"
        
        if self.scholarship_options:
            scholarship_names = [s.name for s in self.scholarship_options if s.name and s.name != "NA"]
            info["scholarships"] = ", ".join(scholarship_names) if scholarship_names else "merit-based scholarships"
        else:
            info["scholarships"] = "merit-based scholarships"
        
        return info

    def _extract_numeric_value(self, amount_str: str) -> float:
        """Extract numeric value from amount string for comparison."""
        try:
            import re
            numbers = re.findall(r'\d+', amount_str.replace(',', ''))
            return float(numbers[0]) if numbers else 0
        except:
            return 0
