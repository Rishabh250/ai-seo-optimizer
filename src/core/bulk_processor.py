"""
Unified bulk content processing framework.

This module consolidates the duplicate logic from all bulk generation scripts
into a single, configurable, and maintainable framework.
"""
import asyncio
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..database.manager import DatabaseManager
from ..models.generator import GeneratorConfig
from ..services.ai_validation_service import AIValidationService
from ..services.content_analysis_service import ContentAnalysisService
from ..services.markdown_converter_service import MarkdownConverterService
from ..utils.exceptions import (
    CollegeNotFoundError,
    ContentGenerationError,
    InvalidConfigurationError,
)
from ..utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class ProcessingStatistics:
    """Statistics tracking for bulk processing operations."""
    total_colleges: int = 0
    successful: int = 0
    failed: int = 0
    skipped: int = 0
    saved_to_db: int = 0
    ai_validated: int = 0
    retries: int = 0
    humanized_colleges: int = 0
    start_time: float = field(default_factory=time.time)

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_colleges == 0:
            return 0.0
        return (self.successful / self.total_colleges) * 100

    @property
    def duration(self) -> float:
        """Get total processing duration in seconds."""
        return time.time() - self.start_time

    @property
    def average_per_college(self) -> float:
        """Get average processing time per college."""
        if self.successful == 0:
            return 0.0
        return self.duration / self.successful


@dataclass
class ProcessingOptions:
    """Configuration options for bulk processing."""
    save_to_db: bool = False
    ai_validation: bool = False
    max_retries: int = 3
    delay: float = 1.0
    dry_run: bool = False
    gptzero_api_key: Optional[str] = None
    google_api_key: Optional[str] = None


@dataclass
class ContentResult:
    """Result of content generation for a single college."""
    college_id: int
    success: bool
    content_markdown: Optional[str] = None
    content_html: Optional[str] = None
    ai_score: Optional[float] = None
    ai_percentage: Optional[float] = None
    attempts: int = 1
    error: Optional[str] = None


class BulkContentProcessor:
    """
    Unified bulk content processing framework.

    This class consolidates all the duplicate logic from bulk generation scripts
    into a single, configurable, and maintainable framework.
    """

    # Mapping of content types to their database tab names
    TAB_NAME_MAPPING = {
        "overview": "overview",
        "overview_short": "overview",
        "courses": "all_courses",
        "course_short": "all_courses",
        "fees": "fees",
        "reviews": "reviews",
        "campus": "campus"
    }

    # Content types that save to short tables
    SHORT_CONTENT_TYPES = {"overview_short", "course_short"}

    def __init__(
        self,
        content_type: str,
        generator_factory,
        config: Optional[GeneratorConfig] = None
    ):
        """
        Initialize the bulk processor.

        Args:
            content_type: Type of content to generate (overview, courses, etc.)
            generator_factory: Factory function that creates the appropriate generator
            config: Generator configuration
        """
        self.content_type = content_type
        self.generator_factory = generator_factory
        self.config = config or GeneratorConfig()
        self.stats = ProcessingStatistics()

        # Initialize services
        self.db_manager = None
        self.ai_validation_service = None
        self.content_analysis_service = None
        self.markdown_converter_service = None

    async def _initialize_services(self, options: ProcessingOptions):
        """Initialize required services based on processing options."""
        try:
            # Database manager (always needed) - existing DatabaseManager doesn't have initialize method
            if not self.db_manager:
                self.db_manager = DatabaseManager()

            # AI validation service (if needed)
            if options.ai_validation:
                # Set API key in environment if provided
                if options.gptzero_api_key:
                    import os
                    os.environ['GPTZERO_API_KEY'] = options.gptzero_api_key
                self.ai_validation_service = AIValidationService()

            # Content analysis service (if saving to DB)
            if options.save_to_db:
                self.content_analysis_service = ContentAnalysisService()
                self.markdown_converter_service = MarkdownConverterService()

            logger.info(f"Initialized services for {self.content_type} bulk processing")

        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            raise InvalidConfigurationError(f"Service initialization failed: {e}")

    async def _cleanup_services(self):
        """Clean up initialized services."""
        # Existing DatabaseManager doesn't have a close method, no cleanup needed
        pass

    async def fetch_college_ids(
        self,
        start_from: Optional[int] = None,
        end_at: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        specific_ids: Optional[List[int]] = None
    ) -> List[int]:
        """
        Fetch college IDs based on the specified criteria.

        Args:
            start_from: Start from this college ID
            end_at: End at this college ID
            limit: Maximum number of colleges
            offset: Skip this many colleges
            specific_ids: Process only these specific college IDs

        Returns:
            List of college IDs to process
        """
        if specific_ids:
            return specific_ids

        # Ensure database manager is initialized
        if not self.db_manager:
            self.db_manager = DatabaseManager()

        # Use synchronous connection for compatibility with existing DatabaseManager
        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                query = "SELECT DISTINCT college_id FROM fmc_summary WHERE college_id IS NOT NULL"
                params = []

                # Add range constraints
                if start_from is not None:
                    query += " AND college_id >= %s"
                    params.append(start_from)

                if end_at is not None:
                    query += " AND college_id <= %s"
                    params.append(end_at)

                query += " ORDER BY college_id"

                # Add pagination
                if offset is not None:
                    query += " OFFSET %s"
                    params.append(offset)

                if limit is not None:
                    query += " LIMIT %s"
                    params.append(limit)

                cursor.execute(query, params)
                result = cursor.fetchall()
                return [row[0] for row in result]

    async def _generate_content_for_college(
        self,
        college_id: int,
        options: ProcessingOptions
    ) -> ContentResult:
        """
        Generate content for a single college with retry logic.

        Args:
            college_id: College ID to process
            options: Processing options

        Returns:
            ContentResult with generation results
        """
        best_result = None
        attempts = 0

        while attempts < options.max_retries:
            attempts += 1

            try:
                logger.info(f"🔄 (Attempt {attempts}/{options.max_retries}) Generating {self.content_type} content for college {college_id}")

                # Generate content using the provided factory
                generator = self.generator_factory(self.config)

                # Try different method name patterns based on content type
                method_candidates = [
                    f'generate_{self.content_type}_by_college_id_sync',
                    f'generate_{self.content_type}_by_college_id',
                    'generate_by_college_id_sync',  # For overview generator
                    'generate_by_college_id',       # For overview generator
                    'generate_content_by_college_id_sync',
                    'generate_content_by_college_id'
                ]

                content = None
                for method_name in method_candidates:
                    if hasattr(generator, method_name):
                        method = getattr(generator, method_name)
                        if asyncio.iscoroutinefunction(method):
                            content = await method(college_id)
                        else:
                            content = method(college_id)
                        break

                if content is None:
                    available_methods = [method for method in dir(generator) if not method.startswith('_') and callable(getattr(generator, method))]
                    raise ContentGenerationError(f"No suitable generation method found for {self.content_type}. Available methods: {available_methods}")

                if not content:
                    raise ContentGenerationError("Empty content generated")

                logger.info(f"✅ Successfully generated {self.content_type} for college {college_id} (Attempt {attempts}/{options.max_retries})")

                # Convert to HTML if needed
                html_content = None
                if options.save_to_db and self.markdown_converter_service:
                    conversion_result = self.markdown_converter_service.convert(content)
                    html_content = conversion_result.html

                result = ContentResult(
                    college_id=college_id,
                    success=True,
                    content_markdown=content,
                    content_html=html_content,
                    attempts=attempts
                )

                # AI validation if requested
                if options.ai_validation and self.ai_validation_service:
                    ai_result = await self._validate_content_ai(content, college_id, attempts, options.max_retries)
                    result.ai_score = ai_result['score']
                    result.ai_percentage = ai_result['percentage']

                    # Check if we need to retry for humanization
                    if ai_result['percentage'] > 90.0 and attempts < options.max_retries:
                        logger.warning(f"⚠️ AI score {ai_result['percentage']:.2f}% is too high for college {college_id}")
                        self.stats.retries += 1
                        best_result = result  # Keep this result as backup
                        await asyncio.sleep(1)  # Brief pause before retry
                        continue
                    elif ai_result['percentage'] <= 90.0:
                        logger.info(f"🎯 AI score {ai_result['percentage']:.2f}% is acceptable for college {college_id}")
                        if attempts > 1:
                            self.stats.humanized_colleges += 1

                return result

            except (CollegeNotFoundError, ContentGenerationError) as e:
                logger.error(f"❌ Error generating {self.content_type} for college {college_id} (Attempt {attempts}/{options.max_retries}): {e}")
                if attempts >= options.max_retries:
                    return ContentResult(
                        college_id=college_id,
                        success=False,
                        error=str(e),
                        attempts=attempts
                    )
                await asyncio.sleep(1)
                continue

        # Return best result if all retries failed but we have a backup
        if best_result:
            logger.warning(f"🎭 Using best available result for college {college_id} with AI score: {best_result.ai_percentage:.2f}%")
            return best_result

        return ContentResult(
            college_id=college_id,
            success=False,
            error="Max retries exceeded",
            attempts=attempts
        )

    async def _validate_content_ai(
        self,
        content: str,
        college_id: int,
        attempt: int,
        max_attempts: int
    ) -> Dict:
        """Validate content using AI detection service."""
        logger.info(f"🤖 Running AI validation for college {college_id} (Attempt {attempt}/{max_attempts})")

        validation_result = await self.ai_validation_service.detect_ai_from_text(content)
        ai_score = validation_result.get('ai_detection_score', 0.0)
        ai_percentage = ai_score * 100

        logger.info(f"🤖 AI validation completed for college {college_id} (Attempt {attempt}/{max_attempts}) - Score: {ai_score:.4f}")

        return {
            'score': ai_score,
            'percentage': ai_percentage
        }

    async def _persist_content(
        self,
        result: ContentResult,
        options: ProcessingOptions
    ) -> bool:
        """Persist generated content to the database."""
        if not options.save_to_db or not result.success:
            return False

        try:
            # Get the appropriate tab name for this content type
            tab_name = self.TAB_NAME_MAPPING.get(self.content_type, self.content_type)

            # Persist content analysis if AI validation was performed
            if result.ai_score is not None:
                can_persist = await self.content_analysis_service.persist_content_analysis(
                    college_id=result.college_id,
                    tab_name=self.content_type,
                    ai_detection_score=result.ai_score,
                    content_markdown=result.content_markdown,
                    html_content=result.content_html
                )

                logger.info(f"Persisted content_analysis for college {result.college_id}, tab {self.content_type} (can_persist={can_persist})")

                if not can_persist:
                    logger.info(f"⏭️ Skipping content persistence for college {result.college_id} due to lower AI score")
                    return False

            # Save to appropriate content table
            if self.content_type in self.SHORT_CONTENT_TYPES:
                await self.content_analysis_service.upsert_college_tab_short_content(
                    college_id=result.college_id,
                    tab_name=tab_name,
                    content_markdown=result.content_markdown,
                    html_content=result.content_html,
                )
                logger.info(f"Upserted short tab content for college {result.college_id}, tab {tab_name}")
            else:
                await self.content_analysis_service.upsert_college_tab_content(
                    college_id=result.college_id,
                    tab_name=tab_name,
                    content_markdown=result.content_markdown,
                    html_content=result.content_html,
                )
                logger.info(f"Upserted tab content for college {result.college_id}, tab {tab_name}")

            return True

        except Exception as e:
            logger.error(f"Error persisting content for college {result.college_id}: {e}")
            return False

    async def process_colleges(
        self,
        college_ids: List[int],
        options: ProcessingOptions
    ) -> ProcessingStatistics:
        """
        Process multiple colleges with the specified options.

        Args:
            college_ids: List of college IDs to process
            options: Processing options

        Returns:
            ProcessingStatistics with results
        """
        await self._initialize_services(options)

        try:
            self.stats.total_colleges = len(college_ids)
            self.stats.start_time = time.time()

            logger.info(f"🚀 Starting bulk {self.content_type} generation for {len(college_ids)} colleges")
            logger.info(f"⏱️ Delay between requests: {options.delay} seconds")
            logger.info(f"💾 Database saving: {'ENABLED' if options.save_to_db else 'DISABLED'}")
            logger.info(f"🤖 AI validation: {'ENABLED' if options.ai_validation else 'DISABLED'}")
            logger.info(f"🎭 Humanization retries: {options.max_retries} attempts for AI scores >90%")

            if options.dry_run:
                logger.info("🔍 DRY RUN MODE - No content will be generated")
                for i, college_id in enumerate(college_ids):
                    logger.info(f"  {i+1}. College ID: {college_id}")
                return self.stats

            for i, college_id in enumerate(college_ids):
                logger.info(f"📊 Progress: {i+1}/{len(college_ids)} ({((i+1)/len(college_ids)*100):.1f}%) - College ID: {college_id}")
                logger.info(f"📚 Generating {self.content_type} for college ID: {college_id}")

                # Generate content
                result = await self._generate_content_for_college(college_id, options)

                if result.success:
                    self.stats.successful += 1

                    # Persist to database if requested
                    if await self._persist_content(result, options):
                        self.stats.saved_to_db += 1
                        logger.info(f"💾 Successfully saved to database for college {college_id}")

                    if result.ai_score is not None:
                        self.stats.ai_validated += 1
                        logger.info(f"📊 Using {self.content_type} content for college {college_id} with final AI score: {result.ai_percentage:.2f}%")
                else:
                    self.stats.failed += 1
                    logger.error(f"❌ Failed to generate {self.content_type} for college {college_id}: {result.error}")

                # Delay between requests
                if i < len(college_ids) - 1:
                    await asyncio.sleep(options.delay)

            return self.stats

        finally:
            await self._cleanup_services()

    def print_summary(self):
        """Print a detailed summary of processing results."""
        logger.info("=" * 70)
        logger.info(f"📈 ENHANCED BULK {self.content_type.upper()} GENERATION SUMMARY")
        logger.info("=" * 70)
        logger.info(f"🎯 Total Colleges: {self.stats.total_colleges}")
        logger.info(f"✅ Successful: {self.stats.successful}")
        logger.info(f"❌ Failed: {self.stats.failed}")
        logger.info(f"⏭️ Skipped: {self.stats.skipped}")
        logger.info(f"💾 Saved to DB: {self.stats.saved_to_db}")
        logger.info(f"🤖 AI Validated: {self.stats.ai_validated}")
        logger.info(f"🔄 Retries Made: {self.stats.retries}")
        logger.info(f"🎭 Humanized Colleges: {self.stats.humanized_colleges}")
        logger.info(f"📊 Success Rate: {self.stats.success_rate:.1f}%")
        logger.info(f"⏱️ Total Duration: {self.stats.duration:.1f} seconds")
        logger.info(f"🔄 Average per College: {self.stats.average_per_college:.1f} seconds")
        logger.info("=" * 70)

        if self.stats.failed == 0:
            logger.info("🎉 All colleges processed successfully!")
        else:
            logger.warning(f"⚠️ {self.stats.failed} colleges failed to process")