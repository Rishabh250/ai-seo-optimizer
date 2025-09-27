"""
Data models for content generator configuration.
"""
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class GeneratorConfig:
    """Configuration for the content generator."""
    api_key: Optional[str] = None
    model: str = "gemini-2.5-flash"
    temperature: float = 0.6

    @classmethod
    def from_env(cls, api_key: Optional[str] = None) -> "GeneratorConfig":
        """Create configuration with optional API key override."""
        return cls(api_key=api_key)


@dataclass
class PromptVariables:
    """Variables for prompt template."""
    college_id: str
    college_name: str
    city: str
    state: str
    establishment_year: str
    campus_area: str
    total_students: str
    faculty_members: str
    faculty_student_ratio: str
    total_courses: str
    departments: str

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for template formatting."""
        return {
            "college_id": self.college_id,
            "college_name": self.college_name,
            "city": self.city,
            "state": self.state,
            "establishment_year": self.establishment_year,
            "campus_area": self.campus_area,
            "total_students": self.total_students,
            "faculty_members": self.faculty_members,
            "faculty_student_ratio": self.faculty_student_ratio,
            "total_courses": self.total_courses,
            "departments": self.departments,
        }
