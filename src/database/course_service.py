"""
Service layer for course data operations.
"""
from ..models.course import CourseData
from ..utils.exceptions import CollegeNotFoundError
from ..utils.logging_config import get_logger
from .manager import get_db_manager

logger = get_logger(__name__)


class CourseService:
    """Service for managing course data operations."""

    def __init__(self):
        self.db = get_db_manager()

    def get_courses_by_college_id(self, college_id: int) -> CourseData:
        """Get course data for a college."""
        try:
            query = """
                SELECT specialization_json, fs.college_name, fs.city, fs.state, fs.cleaned_raw
                FROM fmc_course_specialization
                LEFT JOIN public.fmc_summary fs ON fmc_course_specialization.college_id = fs.college_id
                WHERE fmc_course_specialization.college_id = %(college_id)s
                LIMIT 1
            """
            
            results = self.db.execute_raw_query(query, {"college_id": college_id})
            
            if not results:
                logger.warning(f"No course data found for college ID {college_id}")
                raise CollegeNotFoundError(str(college_id), "ID")
            
            row = results[0]
            specialization_json = row.get('specialization_json', '{}')
            college_name = row.get('college_name', '')
            city = row.get('city', '')
            state = row.get('state', '')
            
            try:
                course_data = CourseData.from_raw_output(
                    specialization_json, 
                    college_name, 
                    city, 
                    state
                )
                logger.info(f"Successfully retrieved course data for college ID {college_id}")
                return course_data
                
            except Exception as e:
                logger.error(f"Error parsing course data for college ID {college_id}: {e}")
                raise Exception(f"Failed to parse course data: {e}")
            
        except CollegeNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error retrieving course data for college ID {college_id}: {e}")
            raise Exception(f"Failed to retrieve course data: {e}")
