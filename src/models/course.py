"""
Data models for course information.
"""
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CourseDetails:
    """Individual course details structure."""
    seats: Optional[str] = None
    level: Optional[str] = None
    domain: Optional[str] = None
    delivery_mode: Optional[str] = None
    specializations: List[str] = field(default_factory=list)
    course_full_name: Optional[str] = None
    duration_in_years: Optional[str] = None
    average_tuition_fee: Optional[str] = None
    eligibility_freshers: List[str] = field(default_factory=list)
    entrance_examinations: List[str] = field(default_factory=list)
    lateral_entry_allowed: Optional[bool] = None
    lateral_entry_eligibility: List[str] = field(default_factory=list)
    specializations_applicable: Optional[bool] = None


@dataclass
class ExtractionMetadata:
    """Metadata about the data extraction."""
    college: Optional[str] = None
    data_completeness: Optional[str] = None
    data_sources_used: Dict[str, List[str]] = field(default_factory=dict)
    extraction_approach: Optional[str] = None


@dataclass
class CourseData:
    """Complete course data structure."""
    college_name: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    course_data: Dict[str, CourseDetails] = field(default_factory=dict)
    extraction_metadata: Optional[ExtractionMetadata] = None

    @classmethod
    def from_raw_output(cls, raw_output: str, college_name: str = "", city: str = "", state: str = "") -> "CourseData":
        """Create CourseData from raw JSON output."""
        try:
            if isinstance(raw_output, str):
                data = json.loads(raw_output)
            else:
                data = raw_output
        except json.JSONDecodeError:
            return cls(college_name=college_name, city=city, state=state)

        # Parse course data
        course_data = {}
        raw_course_data = data.get("course_data", {})
        
        for course_name, course_info in raw_course_data.items():
            if isinstance(course_info, dict):
                course_data[course_name] = CourseDetails(
                    seats=course_info.get("Seats"),
                    level=course_info.get("level"),
                    domain=course_info.get("domain"),
                    delivery_mode=course_info.get("Delivery_Mode"),
                    specializations=course_info.get("Specializations", []),
                    course_full_name=course_info.get("course_full_name"),
                    duration_in_years=course_info.get("Duration_in_years"),
                    average_tuition_fee=course_info.get("Average_tution_fee"),
                    eligibility_freshers=course_info.get("Eligibility_freshers", []),
                    entrance_examinations=course_info.get("Entrance_examinations", []),
                    lateral_entry_allowed=course_info.get("Lateral_entry_allowed"),
                    lateral_entry_eligibility=course_info.get("Lateral_entry_eligibility", []),
                    specializations_applicable=course_info.get("Specializations_Applicable")
                )

        # Parse extraction metadata
        metadata = data.get("extraction_metadata", {})
        extraction_metadata = ExtractionMetadata(
            college=metadata.get("college", college_name),
            data_completeness=metadata.get("data_completeness"),
            data_sources_used=metadata.get("data_sources_used", {}),
            extraction_approach=metadata.get("extraction_approach")
        )

        return cls(
            college_name=extraction_metadata.college or college_name,
            city=city,
            state=state,
            course_data=course_data,
            extraction_metadata=extraction_metadata
        )

    def extract_key_course_info(self) -> Dict[str, str]:
        """Extract key course information for content generation."""
        info = {
            "college_name": self.college_name or "the institution",
            "city": self.city or "",
            "state": self.state or "",
            "establishment_year": "",
            "campus_area": ""
        }

        if not self.course_data:
            info["courses"] = "various courses"
            return info

        # Group courses by level
        levels = {"UG": [], "PG": [], "PhD": [], "Diploma": []}
        all_courses = []
        all_specializations = []
        all_domains = set()

        for course_name, course_details in self.course_data.items():
            all_courses.append(course_name)
            
            if course_details.level:
                level_key = course_details.level
                if level_key in levels:
                    levels[level_key].append(course_name)
            
            if course_details.specializations:
                all_specializations.extend(course_details.specializations)
            
            if course_details.domain:
                all_domains.add(course_details.domain)

        # Create course summary
        course_summary_parts = []
        
        if levels["UG"]:
            course_summary_parts.append(f"UG courses: {', '.join(levels['UG'])}")
        if levels["PG"]:
            course_summary_parts.append(f"PG courses: {', '.join(levels['PG'])}")
        if levels["PhD"]:
            course_summary_parts.append(f"PhD programs: {', '.join(levels['PhD'])}")
        if levels["Diploma"]:
            course_summary_parts.append(f"Diploma courses: {', '.join(levels['Diploma'])}")

        info["courses"] = "; ".join(course_summary_parts) if course_summary_parts else ", ".join(all_courses)
        
        return info
