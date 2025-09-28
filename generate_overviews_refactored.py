#!/usr/bin/env python3
"""
Enhanced Overview Generation Script (Refactored Version)

This script demonstrates the new unified bulk processing framework that eliminates
code duplication and provides a standardized interface across all bulk generation scripts.

BEFORE: 500+ lines of duplicated code across multiple scripts
AFTER: <50 lines using the unified framework

Usage:
    python generate_overviews_refactored.py --start-from 1 --limit 10 --save-to-db --ai-validation
"""
import asyncio

from src.core.cli_framework import create_bulk_cli
from src.core.overview_generator import CollegeOverviewGenerator
from src.models.generator import GeneratorConfig


def create_overview_generator(config: GeneratorConfig) -> CollegeOverviewGenerator:
    """Factory function to create an overview generator."""
    return CollegeOverviewGenerator(config)


async def main():
    """Main entry point for the enhanced overview generation script."""
    # Create the CLI framework with minimal configuration
    cli = create_bulk_cli(
        content_type="overview",
        generator_factory=create_overview_generator,
        description="""
Enhanced College Overview Generation Script with AI Humanization

This script generates comprehensive college overview content using Google's
Generative AI with advanced features including:

- Intelligent AI humanization (auto-retry for AI scores >90%)
- Database persistence with AI score comparison
- Configurable retry attempts and processing delays
- Comprehensive statistics and progress tracking
- Dry-run mode for testing
- Resume processing from any college ID

The script automatically retries content generation up to --max-retries times
when AI detection scores exceed 90%, ensuring more human-like content.
        """
    )

    # Run the CLI framework (handles all argument parsing, validation, and processing)
    await cli.run()


if __name__ == "__main__":
    asyncio.run(main())