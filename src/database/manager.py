import logging
import os
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self, connection_string: Optional[str] = None):
        if connection_string:
            self.connection_string = connection_string
        else:
            self.connection_string = self._build_connection_string()

        self.engine = create_engine(self.connection_string)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def _build_connection_string(self) -> str:
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        database = os.getenv("DB_NAME", "find_my_college")
        username = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD", "1234")

        return f"postgresql://{username}:{password}@{host}:{port}/{database}"

    @contextmanager
    def get_connection(self):
        conn = None
        try:
            conn = psycopg2.connect(self.connection_string)
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def execute_raw_query(self, query: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, params)

                    if query.strip().upper().startswith('SELECT'):
                        results = cur.fetchall()
                        return [dict(row) for row in results]
                    else:
                        conn.commit()
                        return [{"affected_rows": cur.rowcount}]

        except Exception as e:
            logger.error(f"Query execution error: {e}")
            raise

    def fetch_colleges_by_id(self, id: int) -> List[Dict[str, Any]]:
        query = """
            SELECT college_id, college_name, city, state, cleaned_raw
            FROM fmc_summary
            WHERE college_id = %(id)s AND cleaned_raw IS NOT NULL
        """

        return self.execute_raw_query(query, {"id": id})

    def custom_query(self, query: str, params: Optional[Dict] = None) -> List[Dict[str, Any]]:
        return self.execute_raw_query(query, params)

    def fetch_college_ranking_data(self, college_id: int) -> List[Dict[str, Any]]:
        """Fetch comprehensive college data including rankings, accreditation, fees, infrastructure, and summary."""
        query = """
            WITH cleaned_ranking_data AS (
              SELECT
                college_id,
                CASE
                  WHEN j1.ranking_body ~* '(?i)other|awards?[\\s_&]+and[\\s_&]+recognitions?|awards' THEN 'Others'
                  ELSE j1.ranking_body
                END as ranking_body,
                j2.division,
                CASE
                  WHEN j1.ranking_body ~* '(?i)other|awards?[\\s_&]+and[\\s_&]+recognitions?|awards' THEN ''
                  -- removing negative remarks and invalid entries
                  WHEN j2.rank ~* 'not valid|not ranked|not participated|no specific|n/a|na|null|.*not.*|.*Data Submitted.*|.*participat.*|.*ranking found.*|no .*' THEN NULL
                  -- Remove equal signs
                  WHEN j2.rank LIKE '%=%' THEN REGEXP_REPLACE(j2.rank, '=', '', 'g')
                  -- to clean the citations, if present
                  WHEN j2.rank ~ '\\[.*?\\]' OR j2.rank ~ '\\(.*?\\)' THEN
                    TRIM(REGEXP_REPLACE(
                      REGEXP_REPLACE(j2.rank, '\\[.*?\\]', '', 'g'),
                      '\\(.*?\\)', '', 'g'
                    ))
                  WHEN j2.rank LIKE '{%' AND j2.rank LIKE '%}' THEN NULL
                  -- Remove long text descriptions (assuming >50 chars is "long")
                  WHEN LENGTH(j2.rank) > 40 THEN NULL
                  ELSE j2.rank
                END AS cleaned_rank,
                j2.rank as original_rank,
                COALESCE(LENGTH(j2.rank), 0) AS "check"
              FROM
                fmc_college_ranking_accr,
                jsonb_each((raw_output->>'rankings_data')::jsonb) AS j1(ranking_body, ranking_data),
                jsonb_each_text(j1.ranking_data) AS j2(division, rank)
              WHERE
                raw_output->>'rankings_data' IS NOT NULL
                AND jsonb_typeof((raw_output->>'rankings_data')::jsonb) = 'object'
                AND jsonb_typeof(j1.ranking_data) = 'object'
                AND college_id = %(college_id)s
            ),
            ranking_cte AS (
              SELECT
                college_id,
                ranking_body,
                division,
                cleaned_rank,
                original_rank,
                CASE
                  WHEN cleaned_rank ~ '^\d+$' THEN 'int'
                  ELSE 'string'
                END AS rank_type,
                "check"
              FROM cleaned_ranking_data
              WHERE cleaned_rank IS NOT NULL
                AND cleaned_rank != ''
                AND TRIM(cleaned_rank) != ''
            ),
            rankings_aggregated AS (
              SELECT
                college_id,
                jsonb_agg(json_build_object(
                  'college_id', college_id,
                  'ranking_body', ranking_body,
                  'division', division,
                  'rank', cleaned_rank,
                  'original_rank', original_rank,
                  'data_type', rank_type
                )) as cleaned_json_object
              FROM ranking_cte
              GROUP BY college_id
            ),
            cleaned_accreditation AS (
              SELECT
                college_id,
                UPPER(REPLACE(key, '_', ' ')) AS accred_body,
                CASE
                  WHEN value ->> 'grade' = 'NA' OR value ->> 'grade' IS NULL
                  THEN '-'
                  ELSE value ->> 'grade'
                END as grade,
                value ->> 'status' AS status,
                value->>'logo_url' as logo,
                value->>'full_name' as full_name
              FROM fmc_college_ranking_accr,
                jsonb_each(accreditation_with_logo) AS acc(key, value)
              WHERE accreditation_with_logo IS NOT NULL
                AND (new_accr_on_graph IS NULL OR new_accr_on_graph = false)
                AND value ->> 'status' !~* 'invalid|expired|not approved|rejected|not valid|Not Applicable|Not Recognized|Not Accredited|Not Applied|Not Found|NA'
                AND (length(value ->> 'status') > 3 OR (length(value ->> 'status') <= 3 AND value ->> 'grade' !~* 'na|no|n/a'))
                AND college_id = %(college_id)s
            ),
            accreditation_aggregated AS (
              SELECT
                college_id,
                jsonb_agg(json_build_object(
                  'college_id', college_id,
                  'accred_body', accred_body,
                  'grade', grade,
                  'status', status,
                  'logo_url', logo,
                  'full_name', full_name
                )) as cleaned_json_object
              FROM cleaned_accreditation
              GROUP BY college_id
            ),
            degree_fees_aggregated AS (
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
              WHERE college_id = %(college_id)s
              GROUP BY college_id
            ),
            infrastructure_aggregated AS (
              SELECT
                college_id,
                jsonb_agg(json_build_object(
                  'college_id', college_id,
                  'category3_raw', category3_raw,
                  'extraction_metadata', category3_raw->'extraction_metadata'
                )) as cleaned_json_object
              FROM fmc_infrastructure
              WHERE college_id = %(college_id)s
              GROUP BY college_id
            ),
            summary_aggregated AS (
              SELECT
                college_id,
                jsonb_agg(json_build_object(
                  'college_id', college_id,
                  'summary_data', raw_output,
                  'cleaned_summary', cleaned_raw
                )) as cleaned_json_object
              FROM fmc_summary
              WHERE college_id = %(college_id)s
              GROUP BY college_id
            )

            -- Union all sections
            SELECT
              college_id,
              'Ranking' as section_name,
              cleaned_json_object
            FROM rankings_aggregated

            UNION ALL

            SELECT
              college_id,
              'Accreditation' as section_name,
              cleaned_json_object
            FROM accreditation_aggregated

            UNION ALL

            SELECT
              college_id,
              'Degree_Fees' as section_name,
              cleaned_json_object
            FROM degree_fees_aggregated

            UNION ALL

            SELECT
              college_id,
              'Infrastructure' as section_name,
              cleaned_json_object
            FROM infrastructure_aggregated

            UNION ALL

            SELECT
              college_id,
              'Summary' as section_name,
              cleaned_json_object
            FROM summary_aggregated

            ORDER BY section_name;
        """

        try:
            return self.execute_raw_query(query, {"college_id": college_id})
        except Exception as e:
            logger.error(f"Complex query failed, trying fallback approach: {e}")
            # Fallback to individual queries
            try:
                return self._fetch_college_data_fallback(college_id)
            except Exception as fallback_error:
                logger.error(f"Fallback query also failed: {fallback_error}")
                return []

    def _fetch_college_data_fallback(self, college_id: int) -> List[Dict[str, Any]]:
        """Fallback method to fetch college data using separate queries."""
        results = []

        try:
            ranking_query = """
                SELECT
                    college_id,
                    raw_output->>'rankings_data' as rankings_data_json
                FROM fmc_college_ranking_accr
                WHERE college_id = %(college_id)s
                AND raw_output->>'rankings_data' IS NOT NULL
            """
            raw_ranking_result = self.execute_raw_query(ranking_query, {"college_id": college_id})

            if raw_ranking_result:
                import json
                import re

                college_id_val = raw_ranking_result[0]['college_id']
                rankings_json = raw_ranking_result[0]['rankings_data_json']

                if rankings_json:
                    # Handle both string and dict formats
                    if isinstance(rankings_json, str):
                        try:
                            rankings_data = json.loads(rankings_json)
                        except json.JSONDecodeError:
                            logger.error(f"Invalid JSON in rankings_data: {rankings_json}")
                            return []
                    else:
                        rankings_data = rankings_json

                    # Validate that rankings_data is a dictionary
                    if not isinstance(rankings_data, dict):
                        logger.error(f"Rankings data is not a dictionary: {type(rankings_data)}")
                        return []

                    processed_rankings = []

                    for ranking_body, divisions in rankings_data.items():
                        if re.search(r'(?i)other|awards?[\s_&]+and[\s_&]+recognitions?|awards', ranking_body):
                            ranking_body = 'Others'

                        # Skip if divisions is not a dict (e.g., "NA" string)
                        if not isinstance(divisions, dict):
                            continue

                        for division, rank in divisions.items():
                            cleaned_rank = rank
                            original_rank = rank

                            if re.search(r'(?i)not valid|not ranked|not participated|no specific|n/a|na|null|.*not.*|.*Data Submitted.*|.*participat.*|.*ranking found.*|no .*', rank):
                                continue  # Skip invalid entries

                            if rank.endswith('='):
                                cleaned_rank = rank.replace('=', '')

                            if '[' in rank or '(' in rank:
                                cleaned_rank = re.sub(r'\[.*?\]', '', rank)
                                cleaned_rank = re.sub(r'\(.*?\)', '', cleaned_rank)
                                cleaned_rank = cleaned_rank.strip()

                            if rank.startswith('{') and rank.endswith('}'):
                                continue

                            if len(rank) > 40:
                                continue

                            if not cleaned_rank or cleaned_rank.strip() == '':
                                continue

                            data_type = 'int' if re.match(r'^\d+$', cleaned_rank) else 'string'

                            processed_rankings.append({
                                'college_id': college_id_val,
                                'ranking_body': ranking_body,
                                'division': division,
                                'rank': cleaned_rank,
                                'original_rank': original_rank,
                                'data_type': data_type
                            })

                    if processed_rankings:
                        results.append({
                            'college_id': college_id_val,
                            'section_name': 'Ranking',
                            'cleaned_json_object': processed_rankings
                        })

        except Exception as e:
            logger.warning(f"Rankings query failed: {e}")

        try:
            accreditation_query = """
                SELECT
                    college_id,
                    'Accreditation' as section_name,
                    jsonb_agg(
                        jsonb_build_object(
                            'college_id', college_id,
                            'accred_body', UPPER(REPLACE(key, '_', ' ')),
                            'grade', CASE
                                WHEN value ->> 'grade' = 'NA' OR value ->> 'grade' IS NULL
                                THEN '-'
                                ELSE value ->> 'grade'
                            END,
                            'status', value ->> 'status',
                            'logo_url', value->>'logo_url',
                            'full_name', value->>'full_name'
                        )
                    ) as cleaned_json_object
                FROM fmc_college_ranking_accr,
                     jsonb_each(accreditation_with_logo) AS acc(key, value)
                WHERE accreditation_with_logo IS NOT NULL
                  AND (new_accr_on_graph IS NULL OR new_accr_on_graph = false)
                  AND value ->> 'status' !~* 'invalid|expired|not approved|rejected|not valid|Not Applicable|Not Recognized|Not Accredited|Not Applied|Not Found|NA'
                  AND (length(value ->> 'status') > 3 OR (length(value ->> 'status') <= 3 AND value ->> 'grade' !~* 'na|no|n/a'))
                  AND college_id = %(college_id)s
                GROUP BY college_id
            """
            accreditation_result = self.execute_raw_query(accreditation_query, {"college_id": college_id})
            results.extend(accreditation_result)
        except Exception as e:
            logger.warning(f"Accreditation query failed: {e}")

        try:
            summary_query = """
                SELECT
                    college_id,
                    'Summary' as section_name,
                    jsonb_agg(
                        jsonb_build_object(
                            'college_id', college_id,
                            'summary_data', raw_output,
                            'cleaned_summary', cleaned_raw
                        )
                    ) as cleaned_json_object
                FROM fmc_summary
                WHERE college_id = %(college_id)s
                GROUP BY college_id
            """
            summary_result = self.execute_raw_query(summary_query, {"college_id": college_id})
            results.extend(summary_result)
        except Exception as e:
            logger.warning(f"Summary query failed: {e}")

        try:
            fees_query = """
                SELECT
                    college_id,
                    'Degree_Fees' as section_name,
                    jsonb_agg(
                        jsonb_build_object(
                            'college_id', college_id,
                            'degree_name', degree_name,
                            'degree_details', degree_details,
                            'specializations', specializations,
                            'fee_structure', raw_output->'fee_structure',
                            'scholarship_options', raw_output->'scholarship_options',
                            'pwd_accessibility', raw_output->'pwd_accessibility',
                            'reserved_category_fee_impact', raw_output->'reserved_category_fee_impact',
                            'extraction_metadata', raw_output->'extraction_metadata'
                        )
                    ) as cleaned_json_object
                FROM fmc_degree_fees
                WHERE college_id = %(college_id)s
                GROUP BY college_id
            """
            fees_result = self.execute_raw_query(fees_query, {"college_id": college_id})
            results.extend(fees_result)
        except Exception as e:
            logger.warning(f"Fees query failed: {e}")

        try:
            infrastructure_query = """
                SELECT
                    college_id,
                    'Infrastructure' as section_name,
                    jsonb_agg(
                        jsonb_build_object(
                            'college_id', college_id,
                            'category3_raw', category3_raw,
                            'extraction_metadata', category3_raw->'extraction_metadata'
                        )
                    ) as cleaned_json_object
                FROM fmc_infrastructure
                WHERE college_id = %(college_id)s
                GROUP BY college_id
            """
            infrastructure_result = self.execute_raw_query(infrastructure_query, {"college_id": college_id})
            results.extend(infrastructure_result)
        except Exception as e:
            logger.warning(f"Infrastructure query failed: {e}")

        # Name data (using Python-based processing to avoid complex SQL)
        try:
            clean_name_data = self.get_clean_college_name(college_id)
            if clean_name_data:
                results.append({
                    'college_id': college_id,
                    'section_name': 'Name',
                    'cleaned_json_object': [clean_name_data]
                })
        except Exception as e:
            logger.warning(f"Name query failed: {e}")

        return results

    def get_ranking_data_only(self, college_id: int) -> List[Dict[str, Any]]:
        """Get only the ranking data for a college in the specified format."""
        try:
            ranking_query = """
                SELECT
                    raw_output->>'rankings_data' as rankings_data_json
                FROM fmc_college_ranking_accr
                WHERE college_id = %(college_id)s
                AND raw_output->>'rankings_data' IS NOT NULL
            """
            raw_ranking_result = self.execute_raw_query(ranking_query, {"college_id": college_id})

            if raw_ranking_result:
                import json
                import re

                rankings_json = raw_ranking_result[0]['rankings_data_json']

                if rankings_json:
                    # Handle both string and dict formats
                    if isinstance(rankings_json, str):
                        try:
                            rankings_data = json.loads(rankings_json)
                        except json.JSONDecodeError:
                            logger.error(f"Invalid JSON in rankings_data: {rankings_json}")
                            return []
                    else:
                        rankings_data = rankings_json

                    # Validate that rankings_data is a dictionary
                    if not isinstance(rankings_data, dict):
                        logger.error(f"Rankings data is not a dictionary: {type(rankings_data)}")
                        return []

                    processed_rankings = []

                    for ranking_body, divisions in rankings_data.items():
                        if re.search(r'(?i)other|awards?[\s_&]+and[\s_&]+recognitions?|awards', ranking_body):
                            ranking_body = 'Others'

                        # Skip if divisions is not a dict (e.g., "NA" string)
                        if not isinstance(divisions, dict):
                            continue

                        for division, rank in divisions.items():
                            cleaned_rank = rank
                            original_rank = rank

                            if re.search(r'(?i)not valid|not ranked|not participated|no specific|n/a|na|null|.*not.*|.*Data Submitted.*|.*participat.*|.*ranking found.*|no .*', rank):
                                continue

                            if rank.endswith('='):
                                cleaned_rank = rank.replace('=', '')

                            if '[' in rank or '(' in rank:
                                cleaned_rank = re.sub(r'\[.*?\]', '', rank)
                                cleaned_rank = re.sub(r'\(.*?\)', '', cleaned_rank)
                                cleaned_rank = cleaned_rank.strip()

                            if rank.startswith('{') and rank.endswith('}'):
                                continue

                            if len(rank) > 40:
                                continue

                            if not cleaned_rank or cleaned_rank.strip() == '':
                                continue

                            data_type = 'int' if re.match(r'^\d+$', cleaned_rank) else 'string'

                            processed_rankings.append({
                                'ranking_body': ranking_body,
                                'division': division,
                                'rank': cleaned_rank,
                                'original_rank': original_rank,
                                'data_type': data_type
                            })

                    return processed_rankings

        except Exception as e:
            logger.error(f"Ranking data extraction failed: {e}")

        return []

    def get_clean_college_name(self, college_id: int) -> Dict[str, Any]:
        """Get the clean college name, city, and state for a college."""
        try:
            # Get raw data first
            name_query = """
                SELECT
                    college_name,
                    city,
                    state,
                    raw_output
                FROM fmc_clean_names
                WHERE college_id = %(college_id)s
            """
            result = self.execute_raw_query(name_query, {"college_id": college_id})

            if result:
                import json

                row = result[0]
                raw_output = row.get('raw_output', {})

                # Process raw_output if it's a string
                if isinstance(raw_output, str):
                    try:
                        raw_output = json.loads(raw_output)
                    except:
                        raw_output = {}

                # Apply the cleaning logic in Python
                clean_college_name = row['college_name']
                if raw_output.get('Cleaned_Name') and raw_output['Cleaned_Name'].upper() != 'NA':
                    clean_college_name = raw_output['Cleaned_Name']
                elif raw_output.get('Official_Registered_Name'):
                    clean_college_name = raw_output['Official_Registered_Name']

                clean_state = row['state']
                if raw_output.get('State') and raw_output['State'].upper() != 'NA':
                    clean_state = raw_output['State']

                clean_city = row['city']
                if raw_output.get('District') and raw_output['District'].upper() != 'NA':
                    clean_city = raw_output['District']

                return {
                    'college_name': clean_college_name,
                    'city': clean_city,
                    'state': clean_state
                }
            else:
                return {}

        except Exception as e:
            logger.warning(f"Failed to fetch clean college name for college {college_id}: {e}")
            return {}


def get_db_manager(connection_string: Optional[str] = None) -> DatabaseManager:
    return DatabaseManager(connection_string)