"""
Data models for college information.
"""
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class DataSummary:
    """Data summary from college raw data."""
    year_of_establishment: Optional[str] = None
    campus_area_acres: Optional[str] = None
    total_enrolled_students: Optional[str] = None
    total_faculty_members: Optional[str] = None
    faculty_student_ratio: Optional[str] = None
    total_courses_offered: Optional[str] = None
    number_of_departments: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DataSummary":
        """Create DataSummary from dictionary."""
        return cls(
            year_of_establishment=data.get("Year_of_Establishment"),
            campus_area_acres=data.get("Campus_Area_Acres"),
            total_enrolled_students=data.get("Total_Enrolled_Students"),
            total_faculty_members=data.get("Total_Faculty_Members"),
            faculty_student_ratio=data.get("Faculty_Student_ratio"),
            total_courses_offered=data.get("Total_Courses_Offered"),
            number_of_departments=data.get("Number_of_Departments")
        )


@dataclass
class CollegeData:
    """Raw college data from database."""
    college_id: Optional[int] = None
    college_name: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    cleaned_raw: Optional[Dict[str, Any]] = None

    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> "CollegeData":
        """Create CollegeData from database row."""
        return cls(
            college_id=row.get("college_id"),
            college_name=row.get("college_name"),
            city=row.get("city"),
            state=row.get("state"),
            cleaned_raw=row.get("cleaned_raw", {})
        )


@dataclass
class College:
    """Processed college information for content generation."""
    college_id: str
    college_name: str
    city: str
    state: str
    data_summary: DataSummary

    @classmethod
    def from_college_data(cls, college_data: CollegeData) -> "College":
        """Create College from CollegeData."""
        # Extract data summary from cleaned_raw
        cleaned_raw = college_data.cleaned_raw or {}
        data_collection_summary = cleaned_raw.get("Data_Collection_Summary", {})
        data_summary = DataSummary.from_dict(data_collection_summary)

        return cls(
            college_id=str(college_data.college_id or ""),
            college_name=str(college_data.college_name or "the institute"),
            city=str(college_data.city or ""),
            state=str(college_data.state or ""),
            data_summary=data_summary
        )

    def to_prompt_vars(self) -> Dict[str, str]:
        """Convert college data to prompt variables."""
        return {
            "college_id": self.college_id,
            "college_name": self.college_name,
            "city": self.city,
            "state": self.state,
            "establishment_year": str(self.data_summary.year_of_establishment or ""),
            "campus_area": str(self.data_summary.campus_area_acres or ""),
            "total_students": str(self.data_summary.total_enrolled_students or ""),
            "faculty_members": str(self.data_summary.total_faculty_members or ""),
            "faculty_student_ratio": str(self.data_summary.faculty_student_ratio or ""),
            "total_courses": str(self.data_summary.total_courses_offered or ""),
            "departments": str(self.data_summary.number_of_departments or "engineering, management"),
        }
