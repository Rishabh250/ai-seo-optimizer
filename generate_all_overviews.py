#!/usr/bin/env python3
"""
Bulk College Overview Generation Script
Fetches all college IDs from the database and generates overview content for each college in a loop.
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

from src.core.overview_generator import CollegeOverviewGenerator
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


class BulkOverviewGenerator:
    """Handles bulk generation of college overviews."""

    def __init__(self, config: GeneratorConfig, save_to_db: bool = False, ai_validation: bool = False):
        self.config = config
        self.generator = CollegeOverviewGenerator(config)
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
            'ai_validated': 0
        }

    def get_all_college_ids(self) -> List[int]:
        """Fetch all college IDs from the database."""
        try:
            query = """
                SELECT DISTINCT college_id
                FROM fmc_summary
                WHERE college_id IS NOT NULL
                ORDER BY college_id
            """
            result = self.db_manager.execute_raw_query(query)
            college_ids = [row['college_id'] for row in result]
            logger.info(f"Found {len(college_ids)} colleges in database")
            return college_ids
        except Exception as e:
            logger.error(f"Failed to fetch college IDs: {e}")
            return []

    def get_college_ids_with_limit(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[int]:
        """Fetch college IDs with optional limit and offset."""
        try:
            query = """
                SELECT DISTINCT college_id
                FROM fmc_summary
                WHERE college_id IS NOT NULL
                ORDER BY college_id
            """

            if limit:
                query += f" LIMIT {limit}"
            if offset:
                query += f" OFFSET {offset}"

            result = self.db_manager.execute_raw_query(query)
            college_ids = [row['college_id'] for row in result]
            logger.info(f"Found {len(college_ids)} colleges to process")
            return college_ids
        except Exception as e:
            logger.error(f"Failed to fetch college IDs: {e}")
            return []

    async def _persist_generated_result(self, result: ContentResponse, college_id: int, tab_name: str = "overview") -> bool:
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

            # Upsert to college_tab_content
            try:
                await self.content_analysis_service.upsert_college_tab_content(
                    college_id=college_id,
                    tab_name=tab_name,
                    content_markdown=md_text,
                    html_content=html_text,
                )
                logger.info(f"Upserted tab content for college {college_id}, tab {tab_name}")
                return True
            except Exception as e:
                logger.error(f"Failed to upsert tab content for college {college_id}/{tab_name}: {e}")
                return False
        except Exception as e:
            logger.error(f"Failed to persist result for college {college_id}: {e}")
            return False

    async def generate_overview_for_college(self, college_id: int) -> bool:
        """Generate overview for a single college."""
        try:
            logger.info(f"🏫 Generating overview for college ID: {college_id}")

            # Generate the overview
            overview_content = self.generator.generate_by_college_id(college_id)

            if not overview_content:
                logger.warning(f"⚠️ Empty content generated for college {college_id}")
                return False

            logger.info(f"✅ Successfully generated overview for college {college_id}")
            logger.debug(f"Content length: {len(overview_content)} characters")

            # Run AI validation if enabled
            ai_detection = None
            ai_score = None

            if self.ai_validation:
                try:
                    logger.info(f"🤖 Running AI validation for college {college_id}")
                    text_content = self.markdown_converter.md_to_text(overview_content)
                    ai_validation_result = await self.ai_validation_service.detect_ai_from_text(text_content)

                    ai_detection = ai_validation_result
                    ai_score = ai_validation_result.get('overall_score')

                    logger.info(f"🤖 AI validation completed for college {college_id} - Score: {ai_score}")
                    self.stats['ai_validated'] += 1
                except Exception as e:
                    logger.error(f"❌ AI validation failed for college {college_id}: {e}")

            # Save to database if enabled
            if self.save_to_db:
                try:
                    html_content = self.markdown_converter.md_to_html(overview_content)

                    result = ContentResponse(
                        content=overview_content,
                        html_content=html_content,
                        college_name="",  # Could be enhanced to fetch college name
                        metadata={"ai_detection": ai_detection} if ai_detection else {}
                    )

                    success = await self._persist_generated_result(result, college_id, "overview")
                    if success:
                        logger.info(f"💾 Successfully saved to database for college {college_id}")
                        self.stats['saved_to_db'] += 1
                    else:
                        logger.warning(f"⚠️ Failed to save to database for college {college_id}")
                except Exception as e:
                    logger.error(f"❌ Database save failed for college {college_id}: {e}")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to generate overview for college {college_id}: {e}")
            return False

    async def process_colleges(self, college_ids: List[int], delay_seconds: float = 1.0) -> None:
        """Process all colleges with optional delay between requests."""
        self.stats['total'] = len(college_ids)

        logger.info(f"🚀 Starting bulk overview generation for {len(college_ids)} colleges")
        logger.info(f"⏱️ Delay between requests: {delay_seconds} seconds")

        if self.save_to_db:
            logger.info("💾 Database saving: ENABLED")
        if self.ai_validation:
            logger.info("🤖 AI validation: ENABLED")

        start_time = time.time()

        for i, college_id in enumerate(college_ids, 1):
            logger.info(f"📊 Progress: {i}/{len(college_ids)} ({(i/len(college_ids)*100):.1f}%)")

            success = await self.generate_overview_for_college(college_id)

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
        logger.info("=" * 60)
        logger.info("📈 BULK OVERVIEW GENERATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"🎯 Total Colleges: {self.stats['total']}")
        logger.info(f"✅ Successful: {self.stats['successful']}")
        logger.info(f"❌ Failed: {self.stats['failed']}")
        logger.info(f"⏭️ Skipped: {self.stats['skipped']}")

        if self.save_to_db:
            logger.info(f"💾 Saved to DB: {self.stats['saved_to_db']}")
        if self.ai_validation:
            logger.info(f"🤖 AI Validated: {self.stats['ai_validated']}")

        logger.info(f"📊 Success Rate: {(self.stats['successful']/self.stats['total']*100):.1f}%")
        logger.info(f"⏱️ Total Duration: {duration:.1f} seconds")
        logger.info(f"🔄 Average per College: {duration/self.stats['total']:.1f} seconds")
        logger.info("=" * 60)


async def main() -> int:
    """Main function."""
    parser = argparse.ArgumentParser(description="Bulk college overview generation")
    parser.add_argument("--api-key", help="Google API key (or set GOOGLE_API_KEY env var)")
    parser.add_argument("--limit", type=int, help="Maximum number of colleges to process")
    parser.add_argument("--offset", type=int, default=0, help="Number of colleges to skip")
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
    bulk_generator = BulkOverviewGenerator(
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
        else:
            # Fetch from database
            college_ids = bulk_generator.get_college_ids_with_limit(args.limit, args.offset)

        if not college_ids:
            logger.error("❌ No colleges found to process")
            return 1

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
        await bulk_generator.process_colleges(college_ids, args.delay)

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
        logger.error(f"❌ Bulk generation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))