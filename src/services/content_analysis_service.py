"""
Service for saving content analysis results to the database.
"""
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ..database.manager import get_db_manager
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class ContentAnalysisService:
    """Service for managing content analysis database operations."""

    def __init__(self):
        self.db = get_db_manager()

    async def get_connection(self):
        """Get database connection - wrapper for compatibility."""
        return self.db

    async def save_content_analysis_async(self,
                                         public_id: str,
                                         college_id: int,
                                         tab_name: str,
                                         md_content: str,
                                         html_content: str,
                                         ai_detection: Optional[Dict[str, Any]] = None,
                                         ai_score: Optional[float] = None,
                                         university_id: Optional[int] = None,
                                         is_inserted: bool = True) -> Optional[int]:
        """Insert a content analysis record into public.content_analysis and return the new ID.

        Required columns: public_id (UUID), optional: college_id, university_id, tab_name,
        html_content, md_content, ai_detection (jsonb), ai_score (double precision), is_inserted (boolean).
        """
        try:
            ai_detection_json_str: Optional[str] = None
            if ai_detection is not None:
                try:
                    ai_detection_json_str = json.dumps(ai_detection, ensure_ascii=False, allow_nan=False)
                except Exception as ser_err:
                    logger.warning(f"ai_detection not JSON-serializable; skipping storage: {ser_err}")
                    ai_detection_json_str = None

            query = """
                INSERT INTO public.content_analysis
                    (public_id, college_id, university_id, tab_name, html_content, md_content, ai_detection, ai_score, is_inserted, created_at, updated_at)
                VALUES
                    (%(public_id)s, %(college_id)s, %(university_id)s, %(tab_name)s, %(html_content)s, %(md_content)s, %(ai_detection)s::jsonb, %(ai_score)s, %(is_inserted)s, NOW(), NOW())
                RETURNING id
            """
            
            params = {
                'public_id': public_id,
                'college_id': college_id,
                'university_id': university_id,
                'tab_name': tab_name,
                'html_content': html_content,
                'md_content': md_content,
                'ai_detection': ai_detection_json_str,
                'ai_score': ai_score,
                'is_inserted': is_inserted,
            }
            
            result = self.db.execute_raw_query(query, params)
            if result and len(result) > 0:
                new_id = result[0].get('id')
                return int(new_id) if new_id is not None else None
            return None
        except Exception as e:
            logger.error(f"Failed to save content_analysis for college {college_id}: {e}")
            return None

    def save_content_analysis(
        self, 
        college_id: int, 
        tab_name: str, 
        html_content: str, 
        md_content: str, 
        ai_detection: Optional[Dict[str, Any]] = None,
        ai_score: Optional[float] = None,
        university_id: Optional[int] = None,
        is_inserted: bool = True
    ) -> Optional[str]:
        """
        Save content analysis results to the database.
        
        Args:
            college_id: The college ID
            tab_name: The content tab name (overview, courses, fees, etc.)
            html_content: The HTML content
            md_content: The markdown content
            ai_detection: The AI detection results (JSONB)
            ai_score: The AI detection score
            university_id: Optional university ID
            is_inserted: Whether the content has been processed
            
        Returns:
            The public_id of the inserted record, or None if failed
        """
        try:
            public_id = str(uuid.uuid4())
            
            query = """
                INSERT INTO content_analysis (
                    public_id, college_id, university_id, tab_name, 
                    html_content, md_content, ai_detection, ai_score, 
                    is_inserted, created_at, updated_at
                ) VALUES (
                    %(public_id)s, %(college_id)s, %(university_id)s, %(tab_name)s,
                    %(html_content)s, %(md_content)s, %(ai_detection)s, %(ai_score)s,
                    %(is_inserted)s, %(created_at)s, %(updated_at)s
                )
                RETURNING public_id;
            """
            
            now = datetime.now(timezone.utc)
            
            # Convert ai_detection dict to JSON string for PostgreSQL JSONB
            ai_detection_json = None
            if ai_detection is not None:
                ai_detection_json = json.dumps(ai_detection)
            
            params = {
                'public_id': public_id,
                'college_id': college_id,
                'university_id': university_id,
                'tab_name': tab_name,
                'html_content': html_content,
                'md_content': md_content,
                'ai_detection': ai_detection_json,
                'ai_score': ai_score,
                'is_inserted': is_inserted,
                'created_at': now,
                'updated_at': now
            }
            
            result = self.db.execute_raw_query(query, params)
            
            if result:
                logger.info(f"Successfully saved content analysis for college {college_id}, tab {tab_name}")
                return public_id
            else:
                logger.error(f"Failed to save content analysis for college {college_id}, tab {tab_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error saving content analysis for college {college_id}, tab {tab_name}: {e}")
            return None

    def update_ai_detection(self, public_id: str, ai_detection: Dict[str, Any], ai_score: float) -> bool:
        """
        Update AI detection results for an existing record.
        
        Args:
            public_id: The public ID of the record to update
            ai_detection: The AI detection results (JSONB)
            ai_score: The AI detection score
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = """
                UPDATE content_analysis 
                SET ai_detection = %(ai_detection)s, 
                    ai_score = %(ai_score)s,
                    updated_at = %(updated_at)s
                WHERE public_id = %(public_id)s;
            """
            
            # Convert ai_detection dict to JSON string for PostgreSQL JSONB
            ai_detection_json = json.dumps(ai_detection) if ai_detection is not None else None
            
            params = {
                'public_id': public_id,
                'ai_detection': ai_detection_json,
                'ai_score': ai_score,
                'updated_at': datetime.now(timezone.utc)
            }
            
            self.db.execute_raw_query(query, params)
            logger.info(f"Successfully updated AI detection for record {public_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating AI detection for record {public_id}: {e}")
            return False

    def get_content_by_college_and_tab(self, college_id: int, tab_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the latest content analysis record for a college and tab.
        
        Args:
            college_id: The college ID
            tab_name: The content tab name
            
        Returns:
            The latest record or None if not found
        """
        try:
            query = """
                SELECT * FROM content_analysis 
                WHERE college_id = %(college_id)s AND tab_name = %(tab_name)s
                ORDER BY created_at DESC
                LIMIT 1;
            """
            
            params = {
                'college_id': college_id,
                'tab_name': tab_name
            }
            
            result = self.db.execute_raw_query(query, params)
            
            if result:
                return result
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving content analysis for college {college_id}, tab {tab_name}: {e}")
            return None

    def get_college_content_summary(self, college_id: int) -> Dict[str, Any]:
        """
        Get a summary of all content for a college.
        
        Args:
            college_id: The college ID
            
        Returns:
            Summary statistics
        """
        try:
            query = """
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(DISTINCT tab_name) as unique_tabs,
                    COUNT(CASE WHEN ai_detection IS NOT NULL THEN 1 END) as with_ai_detection,
                    ROUND(AVG(ai_score)::numeric, 4) as avg_ai_score,
                    MIN(created_at) as first_created,
                    MAX(created_at) as last_created
                FROM content_analysis 
                WHERE college_id = %(college_id)s;
            """
            
            params = {'college_id': college_id}
            result = self.db.execute_raw_query(query, params)
            
            if result:
                return result
            else:
                return {
                    'total_records': 0,
                    'unique_tabs': 0,
                    'with_ai_detection': 0,
                    'avg_ai_score': None,
                    'first_created': None,
                    'last_created': None
                }
                
        except Exception as e:
            logger.error(f"Error getting college content summary for college {college_id}: {e}")
            return {}

    async def get_google_reviews_processed(self, college_id: int, limit: int = 10) -> List[str]:
        """Fetch processed_output strings from fmc_google_reviews for a college (most recent first).

        Only non-null, non-empty processed outputs are returned, limited by `limit`.
        """
        if not isinstance(college_id, int) or college_id <= 0:
            raise ValueError(f"Invalid college_id: {college_id}")
        if not isinstance(limit, int) or limit <= 0:
            raise ValueError(f"Invalid limit: {limit}")

        try:
            query = """
                SELECT processed_output
                FROM public.fmc_google_reviews
                WHERE college_id = %(college_id)s 
                  AND processed_output IS NOT NULL 
                ORDER BY id DESC
                LIMIT %(limit)s
            """
            
            params = {'college_id': college_id, 'limit': limit}
            result = self.db.execute_raw_query(query, params)

            outputs: List[str] = []
            for row in result:
                value = row.get("processed_output", "")
                if isinstance(value, str):
                    text = value.strip()
                    if text:
                        outputs.append(text)
            return outputs
        except Exception as e:
            logger.error(f"Database error retrieving google reviews for college {college_id}: {e}")
            raise

    async def upsert_college_tab_content(
        self,
        college_id: int,
        tab_name: str,
        content_markdown: str,
        html_content: Optional[str] = None,
    ) -> None:
        """Upsert tab content for a college into public.fmc_content_tabs.

        Schema expectation (create externally if not exists):
          - college_id int primary key
          - <tab>_md text, <tab>_html text for tabs in {overview, all_courses, fees, scholarship, campus, nearby, reviews}
          - timestamps
        """
        if not isinstance(college_id, int) or college_id <= 0:
            raise ValueError(f"Invalid college_id: {college_id}")
        if not tab_name or not isinstance(tab_name, str):
            raise ValueError("tab_name required")

        base_tab = tab_name.strip().lower()
        allowed_tabs = {"overview", "all_courses", "fees", "scholarship", "campus", "nearby", "reviews"}
        if base_tab not in allowed_tabs:
            base_tab = "overview"

        md_col = f"{base_tab}_md"
        html_col = f"{base_tab}_html"

        try:
            query = f"""
                INSERT INTO public.fmc_content_tabs (college_id, {md_col}, {html_col}, updated_at)
                VALUES (%(college_id)s, %(md_content)s, %(html_content)s, NOW())
                ON CONFLICT (college_id)
                DO UPDATE SET {md_col} = EXCLUDED.{md_col}, {html_col} = EXCLUDED.{html_col}, updated_at = NOW()
            """
            
            params = {
                'college_id': college_id,
                'md_content': content_markdown or "",
                'html_content': html_content or "",
            }
            
            self.db.execute_raw_query(query, params)
            logger.info(f"Successfully upserted content into fmc_content_tabs for college {college_id}, tab {base_tab}")
        except Exception as e:
            logger.error(f"Failed upsert into fmc_content_tabs for college {college_id}, tab {base_tab}: {e}")
            raise

    async def get_last_ai_score(self, college_id: int, tab_name: str) -> Optional[float]:
        """Fetch the most recent non-null ai_score for a college/tab from content_analysis."""
        if not isinstance(college_id, int) or college_id <= 0:
            raise ValueError(f"Invalid college_id: {college_id}")
        if not tab_name or not isinstance(tab_name, str):
            raise ValueError("tab_name required")

        try:
            query = """
                SELECT ai_score
                FROM public.content_analysis
                WHERE college_id = %(college_id)s AND tab_name = %(tab_name)s AND ai_score IS NOT NULL
                ORDER BY created_at DESC
                LIMIT 1
            """
            
            params = {'college_id': college_id, 'tab_name': tab_name}
            result = self.db.execute_raw_query(query, params)
            
            if result and len(result) > 0:
                score = result[0].get('ai_score')
                try:
                    return float(score) if score is not None else None
                except Exception:
                    return None
            return None
        except Exception as e:
            logger.error(f"Failed to fetch last ai_score for college {college_id}, tab {tab_name}: {e}")
            return None

    async def get_high_ai_content(self, threshold: float = 0.5, limit: int = 50) -> List[Dict[str, Any]]:
        """Return rows from content_analysis where ai_score >= threshold, ordered by college_id ASC, created_at DESC."""
        try:
            query = """
                SELECT id, college_id, tab_name, ai_score, created_at
                FROM public.content_analysis
                WHERE ai_score IS NOT NULL AND ai_score >= %(threshold)s
                ORDER BY college_id ASC, created_at DESC
                LIMIT %(limit)s
            """
            
            params = {'threshold': threshold, 'limit': limit}
            result = self.db.execute_raw_query(query, params)
            
            return [dict(r) for r in result] if result else []
        except Exception as e:
            logger.error(f"Failed to fetch high AI content rows: {e}")
            return []

    async def upsert_college_tab_short_content(
        self,
        college_id: int,
        tab_name: str,
        content_markdown: str,
        html_content: Optional[str] = None,
    ) -> None:
        """Upsert short tab content for a college into public.fmc_content_tabs_short.

        Expects columns: <tab>_short_md and <tab>_short_html for tabs in
        {overview, all_courses, fees, scholarship, campus, nearby, reviews}.
        """
        if not isinstance(college_id, int) or college_id <= 0:
            raise ValueError(f"Invalid college_id: {college_id}")
        if not tab_name or not isinstance(tab_name, str):
            raise ValueError("tab_name required")

        name = tab_name.strip().lower()
        # Accept either base or *_short; normalise to base
        base_tab = name[:-6] if name.endswith("_short") else name
        allowed_tabs = {"overview", "all_courses", "fees", "scholarship", "campus", "nearby", "reviews"}
        if base_tab not in allowed_tabs:
            base_tab = "overview"

        md_col = f"{base_tab}_short_md"
        html_col = f"{base_tab}_short_html"

        try:
            query = f"""
                INSERT INTO public.fmc_content_tabs_short (college_id, {md_col}, {html_col}, updated_at)
                VALUES (%(college_id)s, %(md_content)s, %(html_content)s, NOW())
                ON CONFLICT (college_id)
                DO UPDATE SET {md_col} = EXCLUDED.{md_col}, {html_col} = EXCLUDED.{html_col}, updated_at = NOW()
            """
            
            params = {
                'college_id': college_id,
                'md_content': content_markdown or "",
                'html_content': html_content or "",
            }
            
            self.db.execute_raw_query(query, params)
            logger.info(f"Successfully upserted short content into fmc_content_tabs_short for college {college_id}, tab {base_tab}")
        except Exception as e:
            logger.error(f"Failed upsert into fmc_content_tabs_short for college {college_id}, tab {base_tab}: {e}")
            raise
