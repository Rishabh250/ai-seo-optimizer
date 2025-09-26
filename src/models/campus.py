"""
Data models for campus infrastructure information.
"""
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class CampusFacility:
    """Individual campus facility structure."""
    facility_name: str = ""
    facility_id: str = ""
    features: List[str] = field(default_factory=list)
    summary_paragraph: str = ""
    summary_bullet_points: List[str] = field(default_factory=list)
    data_source: str = ""
    infrastructure_category: str = ""


@dataclass
class CampusCategory:
    """Campus category with multiple facilities."""
    category_name: str = ""
    facilities: List[CampusFacility] = field(default_factory=list)


@dataclass
class CampusMetadata:
    """Metadata about campus data extraction."""
    college: str = ""
    location: str = ""
    institution_type: str = ""
    academic_year_data: str = ""
    data_completeness_percentage: str = ""
    extraction_date: str = ""


@dataclass
class CampusData:
    """Complete campus infrastructure data structure."""
    college_name: str = ""
    location: str = ""
    categories: Dict[str, List[CampusFacility]] = field(default_factory=dict)
    metadata: Optional[CampusMetadata] = None

    @classmethod
    def from_raw_output(cls, raw_output: str) -> "CampusData":
        """Create CampusData from raw JSON output."""
        try:
            if isinstance(raw_output, str):
                data = json.loads(raw_output)
            else:
                data = raw_output
        except json.JSONDecodeError:
            return cls()

        # Parse metadata
        metadata_dict = data.get("extraction_metadata", {})
        metadata = CampusMetadata(
            college=metadata_dict.get("college", ""),
            location=metadata_dict.get("location", ""),
            institution_type=metadata_dict.get("institution_type", ""),
            academic_year_data=metadata_dict.get("academic_year_data", ""),
            data_completeness_percentage=metadata_dict.get("data_completeness_percentage", ""),
            extraction_date=metadata_dict.get("data_extraction_date", "")
        )

        # Parse categories and facilities
        categories = {}
        for category_name, facilities_list in data.items():
            if category_name == "extraction_metadata":
                continue
            
            if isinstance(facilities_list, list):
                facilities = []
                for facility_data in facilities_list:
                    if isinstance(facility_data, dict):
                        facility = CampusFacility(
                            facility_name=facility_data.get("facility_name", ""),
                            facility_id=facility_data.get("facilityId", ""),
                            features=facility_data.get("features", []),
                            summary_paragraph=facility_data.get("Summary_paragraph", ""),
                            summary_bullet_points=facility_data.get("Summary_bulletPoints", []),
                            data_source=facility_data.get("data_source", ""),
                            infrastructure_category=facility_data.get("infrastructureCategory", category_name)
                        )
                        facilities.append(facility)
                categories[category_name] = facilities

        return cls(
            college_name=metadata.college,
            location=metadata.location,
            categories=categories,
            metadata=metadata
        )

    def extract_key_campus_info(self) -> Dict[str, Any]:
        """Extract key campus information for content generation."""
        info = {
            "college_name": self.college_name or "the institution",
            "location": self.location or "the campus",
            "total_facilities": 0,
            "major_categories": [],
            "key_features": [],
            "laboratory_count": 0,
            "sports_facilities": [],
            "accommodation_available": False,
            "library_available": False
        }

        # Count facilities and extract key information
        for category_name, facilities in self.categories.items():
            if facilities:
                info["total_facilities"] += len(facilities)
                info["major_categories"].append(category_name)
                
                # Extract specific information
                if "Library" in category_name:
                    info["library_available"] = True
                    for facility in facilities:
                        if facility.features:
                            info["key_features"].extend(facility.features[:2])  # Top 2 features
                
                elif "Laboratories" in category_name:
                    info["laboratory_count"] = len(facilities)
                    for facility in facilities:
                        if facility.facility_name:
                            info["key_features"].append(f"{facility.facility_name}")
                
                elif "Sports" in category_name:
                    for facility in facilities:
                        if facility.facility_name:
                            info["sports_facilities"].append(facility.facility_name)
                
                elif "Hostel" in category_name:
                    info["accommodation_available"] = True

        # Limit features to prevent overwhelming content
        info["key_features"] = info["key_features"][:8]
        info["sports_facilities"] = info["sports_facilities"][:5]
        info["major_categories"] = info["major_categories"][:6]

        return info

    def get_facilities_by_category(self, category: str) -> List[CampusFacility]:
        """Get all facilities for a specific category."""
        return self.categories.get(category, [])

    def get_all_facility_names(self) -> List[str]:
        """Get names of all facilities across categories."""
        names = []
        for facilities in self.categories.values():
            for facility in facilities:
                if facility.facility_name:
                    names.append(facility.facility_name)
        return names
