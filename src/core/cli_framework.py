"""
Unified CLI framework for bulk generation scripts.

This module provides a standardized command-line interface that eliminates
duplicate argument parsing across all bulk generation scripts.
"""
import argparse
import os
from typing import Callable, List, Optional

from ..models.generator import GeneratorConfig
from ..utils.logging_config import get_logger
from .bulk_processor import BulkContentProcessor, ProcessingOptions

logger = get_logger(__name__)


class BulkCLIFramework:
    """
    Unified command-line interface framework for bulk content generation.

    This class eliminates the duplicate CLI logic across all bulk generation scripts
    by providing a standardized interface and argument handling.
    """

    def __init__(
        self,
        content_type: str,
        generator_factory: Callable,
        script_description: str
    ):
        """
        Initialize the CLI framework.

        Args:
            content_type: Type of content being generated (overview, courses, etc.)
            generator_factory: Factory function that creates the appropriate generator
            script_description: Description for the CLI help text
        """
        self.content_type = content_type
        self.generator_factory = generator_factory
        self.script_description = script_description
        self.parser = self._create_argument_parser()

    def _create_argument_parser(self) -> argparse.ArgumentParser:
        """Create the standardized argument parser."""
        parser = argparse.ArgumentParser(
            description=self.script_description,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=f"""
Examples:
  # Generate {self.content_type} content for colleges starting from ID 1
  python {self._get_script_name()} --start-from 1 --limit 10

  # Generate with database saving and AI validation
  python {self._get_script_name()} --start-from 1 --limit 10 --save-to-db --ai-validation

  # Process a specific range of colleges
  python {self._get_script_name()} --start-from 100 --end-at 200

  # Process specific college IDs
  python {self._get_script_name()} --college-ids "1,4,5,10"

  # Dry run to see what would be processed
  python {self._get_script_name()} --start-from 1 --limit 5 --dry-run

  # Generate with custom retry attempts for AI humanization
  python {self._get_script_name()} --start-from 1 --limit 10 --max-retries 5

Processing Options:
  The script supports intelligent AI humanization where content with AI detection
  scores >90% is automatically regenerated up to --max-retries times to achieve
  more human-like content.
            """
        )

        # College selection arguments
        college_group = parser.add_argument_group('College Selection')
        college_group.add_argument(
            '--start-from',
            type=int,
            help='Start processing from this college ID'
        )
        college_group.add_argument(
            '--end-at',
            type=int,
            help='End processing at this college ID (inclusive)'
        )
        college_group.add_argument(
            '--limit',
            type=int,
            help='Maximum number of colleges to process'
        )
        college_group.add_argument(
            '--offset',
            type=int,
            help='Skip this many colleges from the start'
        )
        college_group.add_argument(
            '--college-ids',
            type=str,
            help='Comma-separated list of specific college IDs to process (e.g., "1,4,5,10")'
        )

        # Processing options
        processing_group = parser.add_argument_group('Processing Options')
        processing_group.add_argument(
            '--save-to-db',
            action='store_true',
            help='Save generated content to database'
        )
        processing_group.add_argument(
            '--ai-validation',
            action='store_true',
            help='Run AI detection validation on generated content'
        )
        processing_group.add_argument(
            '--max-retries',
            type=int,
            default=3,
            help='Maximum retry attempts for AI scores >90%% (default: 3)'
        )
        processing_group.add_argument(
            '--delay',
            type=float,
            default=1.0,
            help='Delay between requests in seconds (default: 1.0)'
        )
        processing_group.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be processed without generating content'
        )

        # API configuration
        api_group = parser.add_argument_group('API Configuration')
        api_group.add_argument(
            '--api-key',
            help='Google AI API key (overrides environment variable)'
        )
        api_group.add_argument(
            '--gptzero-api-key',
            help='GPTZero API key for AI validation (overrides environment variable)'
        )

        # Model configuration
        model_group = parser.add_argument_group('Model Configuration')
        model_group.add_argument(
            '--model',
            default='gemini-2.5-flash',
            help='AI model to use (default: gemini-2.5-flash)'
        )
        model_group.add_argument(
            '--temperature',
            type=float,
            default=0.3,
            help='Model temperature (default: 0.3)'
        )

        return parser

    def _get_script_name(self) -> str:
        """Get the script name for help text."""
        return f"generate_{self.content_type}_from.py"

    def _parse_college_ids(self, college_ids_str: str) -> List[int]:
        """Parse comma-separated college IDs string."""
        try:
            return [int(id_.strip()) for id_ in college_ids_str.split(',') if id_.strip()]
        except ValueError as e:
            raise argparse.ArgumentTypeError(f"Invalid college IDs format: {e}")

    def _validate_arguments(self, args) -> None:
        """Validate argument combinations."""
        # Check for conflicting college selection options
        college_selection_count = sum([
            args.start_from is not None,
            args.college_ids is not None
        ])

        if college_selection_count == 0:
            raise argparse.ArgumentError(
                None,
                "Must specify either --start-from or --college-ids"
            )

        if college_selection_count > 1:
            raise argparse.ArgumentError(
                None,
                "Cannot specify both --start-from and --college-ids"
            )

        # Validate range arguments
        if args.start_from is not None and args.end_at is not None:
            if args.start_from > args.end_at:
                raise argparse.ArgumentError(
                    None,
                    "--start-from cannot be greater than --end-at"
                )

        # Validate retry attempts
        if args.max_retries < 1:
            raise argparse.ArgumentError(
                None,
                "--max-retries must be at least 1"
            )

        # Validate delay
        if args.delay < 0:
            raise argparse.ArgumentError(
                None,
                "--delay cannot be negative"
            )

        # AI validation requires API key
        if args.ai_validation:
            gptzero_key = args.gptzero_api_key or os.getenv('GPTZERO_API_KEY')
            if not gptzero_key:
                raise argparse.ArgumentError(
                    None,
                    "AI validation requires --gptzero-api-key or GPTZERO_API_KEY environment variable"
                )

    def _create_generator_config(self, args) -> GeneratorConfig:
        """Create generator configuration from CLI arguments."""
        api_key = args.api_key or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("Google AI API key required. Set GOOGLE_API_KEY environment variable or use --api-key")

        return GeneratorConfig(
            api_key=api_key,
            model=args.model,
            temperature=args.temperature
        )

    def _create_processing_options(self, args) -> ProcessingOptions:
        """Create processing options from CLI arguments."""
        return ProcessingOptions(
            save_to_db=args.save_to_db,
            ai_validation=args.ai_validation,
            max_retries=args.max_retries,
            delay=args.delay,
            dry_run=args.dry_run,
            gptzero_api_key=args.gptzero_api_key or os.getenv('GPTZERO_API_KEY'),
            google_api_key=args.api_key or os.getenv('GOOGLE_API_KEY')
        )

    async def _get_college_ids(self, args, processor: BulkContentProcessor) -> List[int]:
        """Get the list of college IDs to process based on arguments."""
        if args.college_ids:
            specific_ids = self._parse_college_ids(args.college_ids)
            logger.info(f"Found {len(specific_ids)} specific college IDs")
            return specific_ids

        # Fetch college IDs from database
        college_ids = await processor.fetch_college_ids(
            start_from=args.start_from,
            end_at=args.end_at,
            limit=args.limit,
            offset=args.offset
        )

        if not college_ids:
            logger.warning("No colleges found matching the specified criteria")
            return []

        # Log range information
        if args.start_from is not None:
            end_info = f" to {args.end_at}" if args.end_at else ""
            limit_info = f" (limited to {args.limit})" if args.limit else ""
            logger.info(f"Found {len(college_ids)} colleges in range from {args.start_from}{end_info}{limit_info}")
        else:
            logger.info(f"Found {len(college_ids)} colleges")

        # Display range for user confirmation
        if college_ids:
            logger.info(f"📋 College ID range: {min(college_ids)} to {max(college_ids)}")

        return college_ids

    async def run(self, argv: Optional[List[str]] = None):
        """
        Run the bulk generation process with the provided arguments.

        Args:
            argv: Command line arguments (uses sys.argv if None)
        """
        try:
            # Parse arguments
            args = self.parser.parse_args(argv)
            self._validate_arguments(args)

            # Create configuration
            config = self._create_generator_config(args)
            options = self._create_processing_options(args)

            # Initialize processor
            processor = BulkContentProcessor(
                content_type=self.content_type,
                generator_factory=self.generator_factory,
                config=config
            )

            # Get college IDs to process
            college_ids = await self._get_college_ids(args, processor)

            if not college_ids:
                logger.error("No colleges to process")
                return

            if args.dry_run:
                logger.info(f"Would process {len(college_ids)} colleges:")
                for i, college_id in enumerate(college_ids[:10]):  # Show first 10
                    logger.info(f"  {i+1}. College ID: {college_id}")
                if len(college_ids) > 10:
                    logger.info(f"  ... and {len(college_ids) - 10} more")
                return

            # Process colleges
            stats = await processor.process_colleges(college_ids, options)

            # Print summary
            processor.print_summary()

        except KeyboardInterrupt:
            logger.info("\n🛑 Process interrupted by user")
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            raise


def create_bulk_cli(
    content_type: str,
    generator_factory: Callable,
    description: str
) -> BulkCLIFramework:
    """
    Factory function to create a bulk CLI framework.

    Args:
        content_type: Type of content being generated
        generator_factory: Factory function for the generator
        description: CLI description

    Returns:
        Configured BulkCLIFramework instance
    """
    return BulkCLIFramework(
        content_type=content_type,
        generator_factory=generator_factory,
        script_description=description
    )