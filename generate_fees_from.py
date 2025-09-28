#!/usr/bin/env python3
"""
Enhanced Fees Generation Script with AI Humanization

This script generates comprehensive fees content using Google's Generative AI
with advanced features including:

- Intelligent AI humanization (auto-retry for AI scores >90%)
- Database persistence with AI score comparison
- Configurable retry attempts and processing delays
- Comprehensive statistics and progress tracking
- Dry-run mode for testing
- Resume processing from any college ID

The script automatically retries content generation up to --max-retries times
when AI detection scores exceed 90%, ensuring more human-like content.

Usage:
    python generate_fees_from.py --start-from 1 --limit 10 --save-to-db --ai-validation
    python generate_fees_from.py --start-from 100 --limit 50 --max-retries 5 --delay 2.0
    python generate_fees_from.py --college-ids "1,4,5,10" --save-to-db --ai-validation
"""

import argparse
import asyncio
import os
import sys
import time
from typing import List, Optional

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.fees_generator import FeesContentGenerator
from src.database.manager import DatabaseManager
from src.models.generator import GeneratorConfig
from src.services.ai_validation_service import AIValidationService
from src.services.content_analysis_service import ContentAnalysisService
from src.services.markdown_converter_service import MarkdownConverterService
from src.utils.logging_config import get_logger, setup_logging

logger = get_logger(__name__)

class EnhancedFeesGenerator:
    """Enhanced fees generator with AI humanization and comprehensive statistics."""

    def __init__(self, config: GeneratorConfig):
        """Initialize the enhanced fees generator."""
        self.config = config
        self.generator = FeesContentGenerator(config)
        self.ai_validation_service = None
        self.content_analysis_service = None
        self.markdown_converter_service = None

        # Statistics tracking
        self.stats = {
            'total': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'saved_to_db': 0,
            'ai_validated': 0,
            'retries': 0,
            'humanized_colleges': 0,
            'start_time': time.time()
        }

    async def initialize_services(self, ai_validation: bool = False, save_to_db: bool = False):
        """Initialize required services."""
        if ai_validation:
            self.ai_validation_service = AIValidationService()

        if save_to_db:
            self.content_analysis_service = ContentAnalysisService()
            self.markdown_converter_service = MarkdownConverterService()

    async def generate_fees_for_college(self, college_id: int, max_retries: int = 3) -> bool:
        """
        Generate fees content for a single college with retry mechanism.

        Args:
            college_id: College ID to process
            max_retries: Maximum retry attempts for AI humanization

        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate fees content with retry mechanism
            result = await self.generator.generate_fees_with_retry(
                college_id=college_id,
                max_retries=max_retries,
                ai_validation_service=self.ai_validation_service
            )

            if not result['success']:
                logger.error(f"❌ Failed to generate fees content for college {college_id}")
                return False

            content = result['content']
            ai_score = result.get('ai_score')
            ai_percentage = result.get('ai_percentage')
            attempts = result.get('attempts', 1)
            humanized = result.get('humanized', False)

            # Update statistics
            if attempts > 1:
                self.stats['retries'] += (attempts - 1)
            if humanized and ai_percentage and ai_percentage <= 90.0:
                self.stats['humanized_colleges'] += 1

            logger.info(f"✅ Successfully generated fees for college {college_id} (Attempt {attempts}/{max_retries})")

            # AI validation logging
            if ai_score is not None:
                self.stats['ai_validated'] += 1
                logger.info(f"🤖 AI validation completed for college {college_id} - Score: {ai_score:.4f}")
                if ai_percentage <= 90.0:
                    logger.info(f"🎯 AI score {ai_percentage:.2f}% is acceptable for college {college_id}")
                else:
                    logger.warning(f"⚠️ AI score {ai_percentage:.2f}% is high but using best available content")

            # Save to database if requested
            if self.content_analysis_service:
                try:
                    # Convert to HTML
                    html_content = None
                    if self.markdown_converter_service:
                        conversion_result = self.markdown_converter_service.convert(content)
                        html_content = conversion_result.html

                    # Persist content analysis if AI validation was performed
                    if ai_score is not None:
                        can_persist = await self.content_analysis_service.persist_content_analysis(
                            college_id=college_id,
                            tab_name='fees',
                            ai_detection_score=ai_score,
                            content_markdown=content,
                            html_content=html_content
                        )
                        logger.info(f"Persisted content_analysis for college {college_id}, tab fees (can_persist={can_persist})")

                        if not can_persist:
                            logger.info(f"⏭️ Skipping content persistence for college {college_id} due to lower AI score")
                            return True

                    # Save to main content table
                    await self.content_analysis_service.upsert_college_tab_content(
                        college_id=college_id,
                        tab_name='fees',
                        content_markdown=content,
                        html_content=html_content,
                    )

                    self.stats['saved_to_db'] += 1
                    logger.info(f"💾 Successfully saved to database for college {college_id}")

                except Exception as e:
                    logger.error(f"Error saving to database for college {college_id}: {e}")

            logger.info(f"📊 Using fees content for college {college_id} with final AI score: {ai_percentage:.2f}%" if ai_percentage else f"📊 Using fees content for college {college_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Error processing college {college_id}: {e}")
            return False

    async def fetch_college_ids(self, start_from: Optional[int] = None, end_at: Optional[int] = None,
                              limit: Optional[int] = None, offset: Optional[int] = None,
                              specific_ids: Optional[List[int]] = None) -> List[int]:
        """Fetch college IDs based on criteria."""
        if specific_ids:
            return specific_ids

        db_manager = DatabaseManager()

        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                query = "SELECT DISTINCT college_id FROM fmc_summary WHERE college_id IS NOT NULL"
                params = []

                if start_from is not None:
                    query += " AND college_id >= %s"
                    params.append(start_from)

                if end_at is not None:
                    query += " AND college_id <= %s"
                    params.append(end_at)

                query += " ORDER BY college_id"

                if offset is not None:
                    query += " OFFSET %s"
                    params.append(offset)

                if limit is not None:
                    query += " LIMIT %s"
                    params.append(limit)

                cursor.execute(query, params)
                result = cursor.fetchall()
                return [row[0] for row in result]

    async def process_colleges(self, college_ids: List[int], max_retries: int = 3, delay: float = 1.0,
                             dry_run: bool = False) -> None:
        """Process multiple colleges with fees generation."""
        self.stats['total'] = len(college_ids)
        self.stats['start_time'] = time.time()

        logger.info(f"🚀 Starting bulk fees generation for {len(college_ids)} colleges")
        logger.info(f"⏱️ Delay between requests: {delay} seconds")
        logger.info(f"🎭 Humanization retries: {max_retries} attempts for AI scores >90%")

        if dry_run:
            logger.info("🔍 DRY RUN MODE - No content will be generated")
            for i, college_id in enumerate(college_ids):
                logger.info(f"  {i+1}. College ID: {college_id}")
            return

        for i, college_id in enumerate(college_ids):
            logger.info(f"📊 Progress: {i+1}/{len(college_ids)} ({((i+1)/len(college_ids)*100):.1f}%) - College ID: {college_id}")
            logger.info(f"📚 Generating fees for college ID: {college_id}")

            success = await self.generate_fees_for_college(college_id, max_retries)

            if success:
                self.stats['successful'] += 1
            else:
                self.stats['failed'] += 1

            # Delay between requests (except for the last one)
            if i < len(college_ids) - 1:
                await asyncio.sleep(delay)

    def print_summary(self):
        """Print comprehensive statistics summary."""
        duration = time.time() - self.stats['start_time']
        success_rate = (self.stats['successful'] / self.stats['total'] * 100) if self.stats['total'] > 0 else 0
        avg_per_college = duration / self.stats['successful'] if self.stats['successful'] > 0 else 0

        logger.info("=" * 70)
        logger.info("📈 ENHANCED BULK FEES GENERATION SUMMARY")
        logger.info("=" * 70)
        logger.info(f"🎯 Total Colleges: {self.stats['total']}")
        logger.info(f"✅ Successful: {self.stats['successful']}")
        logger.info(f"❌ Failed: {self.stats['failed']}")
        logger.info(f"⏭️ Skipped: {self.stats['skipped']}")
        logger.info(f"💾 Saved to DB: {self.stats['saved_to_db']}")
        logger.info(f"🤖 AI Validated: {self.stats['ai_validated']}")
        logger.info(f"🔄 Retries Made: {self.stats['retries']}")
        logger.info(f"🎭 Humanized Colleges: {self.stats['humanized_colleges']}")
        logger.info(f"📊 Success Rate: {success_rate:.1f}%")
        logger.info(f"⏱️ Total Duration: {duration:.1f} seconds")
        logger.info(f"🔄 Average per College: {avg_per_college:.1f} seconds")
        logger.info("=" * 70)

        if self.stats['failed'] == 0:
            logger.info("🎉 All colleges processed successfully!")
        else:
            logger.warning(f"⚠️ {self.stats['failed']} colleges failed to process")


async def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Enhanced Fees Generation Script with AI Humanization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate fees content for colleges starting from ID 1
  python generate_fees_from.py --start-from 1 --limit 10

  # Generate with database saving and AI validation
  python generate_fees_from.py --start-from 1 --limit 10 --save-to-db --ai-validation

  # Process a specific range of colleges
  python generate_fees_from.py --start-from 100 --end-at 200

  # Process specific college IDs
  python generate_fees_from.py --college-ids "1,4,5,10"

  # Dry run to see what would be processed
  python generate_fees_from.py --start-from 1 --limit 5 --dry-run

  # Generate with custom retry attempts for AI humanization
  python generate_fees_from.py --start-from 1 --limit 10 --max-retries 5

Processing Options:
  The script supports intelligent AI humanization where content with AI detection
  scores >90% is automatically regenerated up to --max-retries times to achieve
  more human-like content.
        """
    )

    # College selection arguments
    college_group = parser.add_argument_group('College Selection')
    college_group.add_argument('--start-from', type=int, help='Start processing from this college ID')
    college_group.add_argument('--end-at', type=int, help='End processing at this college ID (inclusive)')
    college_group.add_argument('--limit', type=int, help='Maximum number of colleges to process')
    college_group.add_argument('--offset', type=int, help='Skip this many colleges from the start')
    college_group.add_argument('--college-ids', type=str, help='Comma-separated list of specific college IDs to process (e.g., "1,4,5,10")')

    # Processing options
    processing_group = parser.add_argument_group('Processing Options')
    processing_group.add_argument('--save-to-db', action='store_true', help='Save generated content to database')
    processing_group.add_argument('--ai-validation', action='store_true', help='Run AI detection validation on generated content')
    processing_group.add_argument('--max-retries', type=int, default=3, help='Maximum retry attempts for AI scores >90%% (default: 3)')
    processing_group.add_argument('--delay', type=float, default=1.0, help='Delay between requests in seconds (default: 1.0)')
    processing_group.add_argument('--dry-run', action='store_true', help='Show what would be processed without generating content')

    # API configuration
    api_group = parser.add_argument_group('API Configuration')
    api_group.add_argument('--api-key', help='Google AI API key (overrides environment variable)')
    api_group.add_argument('--gptzero-api-key', help='GPTZero API key for AI validation (overrides environment variable)')

    # Model configuration
    model_group = parser.add_argument_group('Model Configuration')
    model_group.add_argument('--model', default='gemini-2.5-flash', help='AI model to use (default: gemini-2.5-flash)')
    model_group.add_argument('--temperature', type=float, default=0.3, help='Model temperature (default: 0.3)')

    args = parser.parse_args()

    # Validate arguments
    if not args.start_from and not args.college_ids:
        parser.error("Must specify either --start-from or --college-ids")

    if args.start_from and args.college_ids:
        parser.error("Cannot specify both --start-from and --college-ids")

    if args.start_from and args.end_at and args.start_from > args.end_at:
        parser.error("--start-from cannot be greater than --end-at")

    # Setup logging
    setup_logging()

    # Get API key
    api_key = args.api_key or os.getenv('GOOGLE_API_KEY')
    if not api_key:
        logger.error("Google AI API key required. Set GOOGLE_API_KEY environment variable or use --api-key")
        return 1

    # Setup GPTZero API key if AI validation is requested
    if args.ai_validation:
        gptzero_key = args.gptzero_api_key or os.getenv('GPTZERO_API_KEY')
        if not gptzero_key:
            logger.error("AI validation requires --gptzero-api-key or GPTZERO_API_KEY environment variable")
            return 1
        if args.gptzero_api_key:
            os.environ['GPTZERO_API_KEY'] = args.gptzero_api_key

    try:
        # Create configuration
        config = GeneratorConfig(
            api_key=api_key,
            model=args.model,
            temperature=args.temperature
        )

        # Initialize enhanced generator
        enhanced_generator = EnhancedFeesGenerator(config)
        await enhanced_generator.initialize_services(
            ai_validation=args.ai_validation,
            save_to_db=args.save_to_db
        )

        # Get college IDs to process
        if args.college_ids:
            college_ids = [int(id_.strip()) for id_ in args.college_ids.split(',') if id_.strip()]
            logger.info(f"Found {len(college_ids)} specific college IDs")
        else:
            college_ids = await enhanced_generator.fetch_college_ids(
                start_from=args.start_from,
                end_at=args.end_at,
                limit=args.limit,
                offset=args.offset
            )

            if not college_ids:
                logger.warning("No colleges found matching the specified criteria")
                return 0

            # Log range information
            if args.start_from is not None:
                end_info = f" to {args.end_at}" if args.end_at else ""
                limit_info = f" (limited to {args.limit})" if args.limit else ""
                logger.info(f"Found {len(college_ids)} colleges in range from {args.start_from}{end_info}{limit_info}")

        # Display processing information
        logger.info(f"📋 College ID range: {min(college_ids)} to {max(college_ids)}")
        logger.info(f"💾 Database saving: {'ENABLED' if args.save_to_db else 'DISABLED'}")
        logger.info(f"🤖 AI validation: {'ENABLED' if args.ai_validation else 'DISABLED'}")

        # Process colleges
        await enhanced_generator.process_colleges(
            college_ids=college_ids,
            max_retries=args.max_retries,
            delay=args.delay,
            dry_run=args.dry_run
        )

        # Print summary
        enhanced_generator.print_summary()

        return 0

    except KeyboardInterrupt:
        logger.info("\n🛑 Process interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)