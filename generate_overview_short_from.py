#!/usr/bin/env python3
"""
Enhanced Bulk College Overview Short Generation Script with Start-From Feature
Fetches college IDs from the database and generates overview_short content starting from a specific point.
"""

import argparse
import asyncio
import logging
import os
import sys
import time
import uuid
from pathlib import Path
from typing import List, Optional

# Add the project root to sys.path
_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from src.core.overview_short_generator import CollegeOverviewShortGenerator
from src.database.manager import DatabaseManager
from src.models.generator import GeneratorConfig
from src.services.ai_validation_service import AIValidationService
from src.services.content_analysis_service import ContentAnalysisService
from src.services.markdown_converter_service import MarkdownConverterService
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def setup_logging() -> None:
    """Setup simple logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


class ContentResponse:
    """Content response structure for compatibility with the persist function."""
    def __init__(self, content: str, html_content: str = None, college_name: str = "", metadata: dict = None):
        self.content = content
        self.html_content = html_content
        self.college_name = college_name
        self.metadata = metadata or {}


class EnhancedBulkOverviewShortGenerator:
    """Handles bulk generation of college overview_short content with start-from capability."""

    def __init__(self, config: GeneratorConfig, save_to_db: bool = False, ai_validation: bool = False):
        self.config = config
        self.generator = CollegeOverviewShortGenerator(config)
        self.db_manager = DatabaseManager()
        self.save_to_db = save_to_db
        self.ai_validation = ai_validation

        # Initialize services if needed
        if self.save_to_db:
            self.content_analysis_service = ContentAnalysisService()
            self.markdown_converter = MarkdownConverterService()
        if self.ai_validation:
            self.ai_validation_service = AIValidationService()

        self.stats = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'saved_to_db': 0,
            'ai_validated': 0,
            'retries': 0,
            'humanized': 0  # Count of colleges that needed humanization retries
        }

    def get_college_ids_from_point(self, start_from: Optional[int] = None, limit: Optional[int] = None) -> List[int]:
        """Fetch college IDs starting from a specific college ID."""
        try:
            base_query = """
                SELECT DISTINCT college_id
                FROM fmc_summary
                WHERE college_id IS NOT NULL
            """

            if start_from:
                base_query += f" AND college_id >= {start_from}"

            base_query += " ORDER BY college_id"

            if limit:
                base_query += f" LIMIT {limit}"

            result = self.db_manager.execute_raw_query(base_query)
            college_ids = [row['college_id'] for row in result]

            start_msg = f" starting from college ID {start_from}" if start_from else ""
            limit_msg = f" (limited to {limit})" if limit else ""
            logger.info(f"Found {len(college_ids)} colleges{start_msg}{limit_msg}")

            return college_ids
        except Exception as e:
            logger.error(f"Failed to fetch college IDs: {e}")
            return []

    def get_college_ids_in_range(self, start_from: int, end_at: Optional[int] = None, limit: Optional[int] = None) -> List[int]:
        """Fetch college IDs in a specific range."""
        try:
            query = """
                SELECT DISTINCT college_id
                FROM fmc_summary
                WHERE college_id IS NOT NULL
                AND college_id >= %(start_from)s
            """

            params = {'start_from': start_from}

            if end_at:
                query += " AND college_id <= %(end_at)s"
                params['end_at'] = end_at

            query += " ORDER BY college_id"

            if limit:
                query += " LIMIT %(limit)s"
                params['limit'] = limit

            result = self.db_manager.execute_raw_query(query, params)
            college_ids = [row['college_id'] for row in result]

            range_msg = f"from {start_from}"
            if end_at:
                range_msg += f" to {end_at}"
            if limit:
                range_msg += f" (limited to {limit})"

            logger.info(f"Found {len(college_ids)} colleges in range {range_msg}")
            return college_ids
        except Exception as e:
            logger.error(f"Failed to fetch college IDs in range: {e}")
            return []

    async def _persist_generated_result(self, result: ContentResponse, college_id: int, tab_name: str = "overview_short") -> bool:
        """Advanced content persistence with AI score comparison and intelligent upserting."""
        try:
            new_ai_detection = (result.metadata or {}).get("ai_detection")
            new_ai_score = None
            if isinstance(new_ai_detection, dict):
                val = new_ai_detection.get("overall_score") or new_ai_detection.get("summary", {}).get("ai_probability_percent")
                try:
                    new_ai_score = float(val) if val is not None else None
                except Exception:
                    new_ai_score = None

            can_persist = True
            try:
                last_score = await self.content_analysis_service.get_last_ai_score(college_id, tab_name)
                if last_score is not None and new_ai_score is not None:
                    can_persist = new_ai_score < last_score
                    logger.info(f"AI score comparison: new={new_ai_score}, last={last_score}, can_persist={can_persist}")
            except Exception as e:
                logger.error(f"Failed to fetch last AI score; proceeding with persistence: {e}")

            md_text = result.content or ""
            html_text = result.html_content
            if not html_text and self.markdown_converter:
                try:
                    html_text = self.markdown_converter.md_to_html(md_text).strip()
                except Exception as e:
                    logger.error(f"HTML generation failed: {e}")
                    html_text = ""

            # Save to content_analysis table
            try:
                public_id = str(uuid.uuid4())
                await self.content_analysis_service.save_content_analysis_async(
                    public_id=public_id,
                    college_id=college_id,
                    tab_name=tab_name,
                    md_content=md_text,
                    html_content=html_text or "",
                    ai_detection=new_ai_detection if self.ai_validation else None,
                    ai_score=new_ai_score,
                    university_id=None,
                    is_inserted=bool(can_persist),
                )
                logger.info(f"Persisted content_analysis for college {college_id}, tab {tab_name} (can_persist={can_persist})")
            except Exception as e:
                logger.error(f"Failed to persist content_analysis for college {college_id}: {e}")
                return False

            if not can_persist:
                logger.info(f"Skipping tab content upsert due to higher AI score for college {college_id}, tab {tab_name}")
                return True

            # Upsert to college_tab_short_content
            try:
                await self.content_analysis_service.upsert_college_tab_short_content(
                    college_id=college_id,
                    tab_name=tab_name,
                    content_markdown=md_text,
                    html_content=html_text,
                )
                logger.info(f"Upserted short tab content for college {college_id}, tab {tab_name}")
                return True
            except Exception as e:
                logger.error(f"Failed to upsert short tab content for college {college_id}/{tab_name}: {e}")
                return False
        except Exception as e:
            logger.error(f"Failed to persist result for college {college_id}: {e}")
            return False

    async def generate_overview_short_for_college(self, college_id: int, max_retries: int = 3) -> bool:
        """Generate overview_short for a single college with AI score retry mechanism."""
        try:
            logger.info(f"📝 Generating overview_short for college ID: {college_id}")

            best_content = None
            best_ai_score = None
            best_ai_detection = None
            attempts = 0

            # Generate content with retry mechanism for high AI scores
            while attempts < max_retries:
                attempts += 1
                attempt_prefix = f"(Attempt {attempts}/{max_retries})" if max_retries > 1 else ""

                logger.info(f"🔄 {attempt_prefix} Generating overview_short content for college {college_id}")

                # Generate the overview_short
                overview_short_content = self.generator.generate_by_college_id(college_id)

                if not overview_short_content:
                    logger.warning(f"⚠️ Empty content generated for college {college_id} on attempt {attempts}")
                    if attempts < max_retries:
                        continue
                    else:
                        return False

                logger.info(f"✅ Successfully generated overview_short for college {college_id} {attempt_prefix}")
                logger.debug(f"Content length: {len(overview_short_content)} characters")

                # Run AI validation if enabled
                ai_detection = None
                ai_score = None

                if self.ai_validation:
                    try:
                        logger.info(f"🤖 Running AI validation for college {college_id} {attempt_prefix}")
                        text_content = self.markdown_converter.md_to_text(overview_short_content)
                        ai_validation_result = await self.ai_validation_service.detect_ai_from_text(text_content)

                        ai_detection = ai_validation_result
                        ai_score = ai_validation_result.get('overall_score')

                        logger.info(f"🤖 AI validation completed for college {college_id} {attempt_prefix} - Score: {ai_score}")
                        self.stats['ai_validated'] += 1

                        # Check if AI score is acceptable (less than 90%)
                        if ai_score is not None:
                            ai_score_percentage = float(ai_score) * 100 if ai_score <= 1.0 else float(ai_score)

                            if ai_score_percentage <= 90.0:
                                logger.info(f"🎯 AI score {ai_score_percentage:.2f}% is acceptable for college {college_id}")
                                best_content = overview_short_content
                                best_ai_score = ai_score
                                best_ai_detection = ai_detection
                                # Track if this college needed humanization (more than 1 attempt)
                                if attempts > 1:
                                    self.stats['humanized'] += 1
                                break
                            else:
                                logger.warning(f"⚠️ AI score {ai_score_percentage:.2f}% is too high for college {college_id}")

                                # Keep track of the best (lowest) score so far
                                if best_ai_score is None or ai_score < best_ai_score:
                                    best_content = overview_short_content
                                    best_ai_score = ai_score
                                    best_ai_detection = ai_detection
                                    logger.info(f"🔄 Saved as best attempt so far (Score: {ai_score_percentage:.2f}%)")

                                if attempts < max_retries:
                                    logger.info(f"🔄 Retrying overview_short generation for college {college_id} (attempt {attempts + 1}/{max_retries})")
                                    self.stats['retries'] += 1
                                    await asyncio.sleep(1)  # Brief pause before retry
                                    continue
                                else:
                                    logger.warning(f"⚠️ Max retries reached for college {college_id}. Using best attempt (Score: {(best_ai_score * 100 if best_ai_score <= 1.0 else best_ai_score):.2f}%)")
                                    # This college needed humanization attempts
                                    self.stats['humanized'] += 1
                                    break
                        else:
                            # No AI score available, use the content
                            best_content = overview_short_content
                            best_ai_detection = ai_detection
                            break

                    except Exception as e:
                        logger.error(f"❌ AI validation failed for college {college_id} {attempt_prefix}: {e}")
                        if not best_content:  # If this is our first attempt and validation failed
                            best_content = overview_short_content
                        break
                else:
                    # No AI validation enabled, use the content
                    best_content = overview_short_content
                    break

            # Use the best content we generated
            if not best_content:
                logger.error(f"❌ No valid content generated for college {college_id} after {attempts} attempts")
                return False

            # Update final stats
            final_score_pct = (best_ai_score * 100 if best_ai_score and best_ai_score <= 1.0 else best_ai_score) if best_ai_score else "N/A"
            logger.info(f"📊 Using overview_short content for college {college_id} with final AI score: {final_score_pct}%")

            # Save to database if enabled
            if self.save_to_db:
                try:
                    html_content = self.markdown_converter.md_to_html(best_content)

                    result = ContentResponse(
                        content=best_content,
                        html_content=html_content,
                        college_name="",
                        metadata={"ai_detection": best_ai_detection} if best_ai_detection else {}
                    )

                    success = await self._persist_generated_result(result, college_id, "overview_short")
                    if success:
                        logger.info(f"💾 Successfully saved to database for college {college_id}")
                        self.stats['saved_to_db'] += 1
                    else:
                        logger.warning(f"⚠️ Failed to save to database for college {college_id}")
                except Exception as e:
                    logger.error(f"❌ Database save failed for college {college_id}: {e}")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to generate overview_short for college {college_id}: {e}")
            return False

    async def process_colleges(self, college_ids: List[int], delay_seconds: float = 1.0, max_retries: int = 3) -> None:
        """Process all colleges with optional delay between requests."""
        self.stats['total'] = len(college_ids)

        logger.info(f"🚀 Starting bulk overview_short generation for {len(college_ids)} colleges")
        logger.info(f"⏱️ Delay between requests: {delay_seconds} seconds")

        if self.save_to_db:
            logger.info("💾 Database saving: ENABLED")
        if self.ai_validation:
            logger.info("🤖 AI validation: ENABLED")
            logger.info(f"🎭 Humanization retries: {max_retries} attempts for AI scores >90%")

        start_time = time.time()

        for i, college_id in enumerate(college_ids, 1):
            logger.info(f"📊 Progress: {i}/{len(college_ids)} ({(i/len(college_ids)*100):.1f}%) - College ID: {college_id}")

            success = await self.generate_overview_short_for_college(college_id, max_retries)

            if success:
                self.stats['successful'] += 1
            else:
                self.stats['failed'] += 1

            # Add delay between requests to avoid overwhelming the API
            if i < len(college_ids) and delay_seconds > 0:
                await asyncio.sleep(delay_seconds)

        end_time = time.time()
        duration = end_time - start_time

        self.print_summary(duration)

    def print_summary(self, duration: float) -> None:
        """Print generation summary statistics."""
        logger.info("=" * 70)
        logger.info("📈 ENHANCED BULK OVERVIEW_SHORT GENERATION SUMMARY")
        logger.info("=" * 70)
        logger.info(f"🎯 Total Colleges: {self.stats['total']}")
        logger.info(f"✅ Successful: {self.stats['successful']}")
        logger.info(f"❌ Failed: {self.stats['failed']}")
        logger.info(f"⏭️ Skipped: {self.stats['skipped']}")

        if self.save_to_db:
            logger.info(f"💾 Saved to DB: {self.stats['saved_to_db']}")
        if self.ai_validation:
            logger.info(f"🤖 AI Validated: {self.stats['ai_validated']}")
            logger.info(f"🔄 Retries Made: {self.stats['retries']}")
            logger.info(f"🎭 Humanized Colleges: {self.stats['humanized']}")

        logger.info(f"📊 Success Rate: {(self.stats['successful']/self.stats['total']*100):.1f}%")
        logger.info(f"⏱️ Total Duration: {duration:.1f} seconds")
        logger.info(f"🔄 Average per College: {duration/self.stats['total']:.1f} seconds")
        logger.info("=" * 70)


async def main() -> int:
    """Main function."""
    parser = argparse.ArgumentParser(description="Enhanced bulk college overview_short generation with start-from capability")
    parser.add_argument("--api-key", help="Google API key (or set GOOGLE_API_KEY env var)")
    parser.add_argument("--limit", type=int, help="Maximum number of colleges to process")
    parser.add_argument("--start-from", type=int, help="Start processing from this college ID")
    parser.add_argument("--end-at", type=int, help="End processing at this college ID")
    parser.add_argument("--delay", type=float, default=1.0,
                        help="Delay in seconds between API calls (default: 1.0)")
    parser.add_argument("--college-ids", type=str,
                        help="Comma-separated list of specific college IDs to process")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be processed without actually generating content")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--save-to-db", action="store_true",
                        help="Save generated content to database")
    parser.add_argument("--ai-validation", action="store_true",
                        help="Run AI validation on generated content")
    parser.add_argument("--gptzero-api-key", help="GPTZero API key for AI validation (or set GPTZERO_API_KEY env var)")
    parser.add_argument("--max-retries", type=int, default=3,
                        help="Maximum retries for content with AI score >90%% (default: 3)")

    args = parser.parse_args()

    # Setup logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    setup_logging()

    # Get API key
    api_key = args.api_key or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("❌ Google API key is required. Set GOOGLE_API_KEY environment variable or use --api-key")
        return 1

    # Set GPTZero API key if provided
    if args.gptzero_api_key:
        os.environ["GPTZERO_API_KEY"] = args.gptzero_api_key

    # Validate AI validation requirements
    if args.ai_validation and not (args.gptzero_api_key or os.getenv("GPTZERO_API_KEY")):
        logger.warning("⚠️ AI validation requested but no GPTZero API key provided. Using default key.")

    # Create configuration
    config = GeneratorConfig(api_key=api_key)

    # Create bulk generator with new options
    bulk_generator = EnhancedBulkOverviewShortGenerator(
        config=config,
        save_to_db=args.save_to_db,
        ai_validation=args.ai_validation
    )

    try:
        # Determine which colleges to process
        if args.college_ids:
            # Process specific college IDs
            college_ids = [int(x.strip()) for x in args.college_ids.split(",")]
            logger.info(f"🎯 Processing specified college IDs: {college_ids}")
        elif args.start_from or args.end_at:
            # Use range-based fetching
            college_ids = bulk_generator.get_college_ids_in_range(
                start_from=args.start_from or 1,
                end_at=args.end_at,
                limit=args.limit
            )
        else:
            # Use start-from with limit
            college_ids = bulk_generator.get_college_ids_from_point(
                start_from=args.start_from,
                limit=args.limit
            )

        if not college_ids:
            logger.error("❌ No colleges found to process")
            return 1

        # Show range info
        if len(college_ids) > 0:
            logger.info(f"📋 College ID range: {min(college_ids)} to {max(college_ids)}")

        # Dry run mode
        if args.dry_run:
            logger.info("🔍 DRY RUN MODE - No content will be generated")
            logger.info(f"Would process {len(college_ids)} colleges:")
            for i, college_id in enumerate(college_ids[:10]):  # Show first 10
                logger.info(f"  {i+1}. College ID: {college_id}")
            if len(college_ids) > 10:
                logger.info(f"  ... and {len(college_ids)-10} more colleges")
            return 0

        # Process colleges
        await bulk_generator.process_colleges(college_ids, args.delay, args.max_retries)

        # Determine exit code based on results
        if bulk_generator.stats['successful'] == bulk_generator.stats['total']:
            logger.info("🎉 All colleges processed successfully!")
            return 0
        elif bulk_generator.stats['successful'] > 0:
            logger.warning(f"⚠️ Partial success: {bulk_generator.stats['successful']}/{bulk_generator.stats['total']} completed")
            return 2
        else:
            logger.error("❌ All colleges failed to process")
            return 1

    except KeyboardInterrupt:
        logger.info("⏹️ Process interrupted by user")
        bulk_generator.print_summary(0)
        return 130
    except Exception as e:
        logger.error(f"❌ Enhanced bulk overview_short generation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))