#!/usr/bin/env python3
"""
Simple AI Content Generator - Clean and minimal implementation
"""

import argparse
import asyncio
import logging
import os
import sys
import uuid
from pathlib import Path
from typing import Any, Optional

_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from src.core.campus_generator import CampusContentGenerator  # noqa: E402
from src.core.course_generator import CourseContentGenerator  # noqa: E402
from src.core.fees_generator import FeesContentGenerator  # noqa: E402
from src.core.overview_generator import CollegeOverviewGenerator  # noqa: E402
from src.core.overview_short_generator import (
    CollegeOverviewShortGenerator,  # noqa: E402
)
from src.core.reviews_generator import ReviewsContentGenerator  # noqa: E402
from src.models.generator import GeneratorConfig  # noqa: E402
from src.services.ai_validation_service import AIValidationService  # noqa: E402
from src.services.content_analysis_service import ContentAnalysisService  # noqa: E402
from src.services.markdown_converter_service import (  # noqa: E402
    MarkdownConverterService,  # noqa: E402
)
from src.utils.logging_config import get_logger  # noqa: E402

logger = get_logger(__name__)


def setup_logging() -> None:
    """Setup simple logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

async def generate_overview(config: GeneratorConfig, college_id: int) -> str:
    """Generate overview content."""
    generator = CollegeOverviewGenerator(config)
    overview = generator.generate_by_college_id(college_id)
    
    return overview


async def generate_fees(config: GeneratorConfig, college_id: int) -> Any:
    """Generate fees content."""
    generator = FeesContentGenerator(config)
    fees_content = generator.generate_fees_by_college_id(college_id)
    
    return fees_content


async def generate_reviews(config: GeneratorConfig, college_id: int) -> str:
    """Generate reviews content."""
    generator = ReviewsContentGenerator(config)
    reviews_content = generator.generate_reviews_by_college_id(college_id)
    return reviews_content


async def generate_courses(config: GeneratorConfig, college_id: int) -> str:
    """Generate courses content."""
    generator = CourseContentGenerator(config)
    return await generator.generate_courses_by_college_id(college_id)


async def generate_campus(config: GeneratorConfig, college_id: int) -> str:
    """Generate campus content."""
    generator = CampusContentGenerator(config)
    return generator.generate_campus_by_college_id(college_id)


async def generate_overview_short(config: GeneratorConfig, college_id: int) -> str:
    """Generate overview short summary content."""
    generator = CollegeOverviewShortGenerator(config)
    return generator.generate_by_college_id(college_id)


class ContentResponse:
    """Content response structure for compatibility with the persist function."""
    def __init__(self, content: str, html_content: str = None, college_name: str = "", metadata: dict = None):
        self.content = content
        self.html_content = html_content
        self.college_name = college_name
        self.metadata = metadata or {}


async def _persist_generated_result(result: ContentResponse, college_id: int, tab_name: str, validate_ai: bool) -> None:
    """Advanced content persistence with AI score comparison and intelligent upserting."""
    database_service = ContentAnalysisService()
    markdown_converter = MarkdownConverterService()
    
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
        last_score = await database_service.get_last_ai_score(college_id, tab_name)
        if last_score is not None and new_ai_score is not None:
            can_persist = new_ai_score < last_score
            logger.info(f"AI score comparison: new={new_ai_score}, last={last_score}, can_persist={can_persist}")
    except Exception as e:
        logger.error(f"Failed to fetch last AI score; proceeding with persistence: {e}")

    md_text = result.content or ""
    html_text = result.html_content
    if not html_text and markdown_converter:
        try:
            html_text = markdown_converter.md_to_html(md_text).strip()
        except Exception as e:
            logger.error(f"HTML generation failed: {e}")
            html_text = ""

    try:
        public_id = str(uuid.uuid4())
        await database_service.save_content_analysis_async(
            public_id=public_id,
            college_id=college_id,
            tab_name=tab_name,
            md_content=md_text,
            html_content=html_text or "",
            ai_detection=new_ai_detection if validate_ai else None,
            ai_score=new_ai_score,
            university_id=None,
            is_inserted=bool(can_persist),
        )
        logger.info(f"Persisted content_analysis for college {college_id}, tab {tab_name} (can_persist={can_persist})")
    except Exception as e:
        logger.error(f"Failed to persist content_analysis for college {college_id}: {e}")

    if not can_persist:
        logger.info(f"Skipping tab content upsert due to higher AI score for college {college_id}, tab {tab_name}")
        return

    try:
        if tab_name.endswith("_short"):
            await database_service.upsert_college_tab_short_content(
                college_id=college_id,
                tab_name=tab_name,
                content_markdown=md_text,
                html_content=html_text,
            )
            logger.info(f"Upserted short tab content for college {college_id}, tab {tab_name}")
        else:
            await database_service.upsert_college_tab_content(
                college_id=college_id,
                tab_name=tab_name,
                content_markdown=md_text,
                html_content=html_text,
            )
            logger.info(f"Upserted tab content for college {college_id}, tab {tab_name}")
    except Exception as e:
        logger.error(f"Failed to upsert tab content for college {college_id}/{tab_name}: {e}")


async def save_content_to_database(
    content: str, 
    college_id: int, 
    tab_name: str, 
    run_ai_validation: bool = False,
    college_name: str = ""
) -> Optional[str]:
    """Save content to database with optional AI validation using advanced persistence logic."""
    if not content:
        logger.warning("No content available to save")
        return None

    try:
        markdown_converter = MarkdownConverterService()
        html_content = markdown_converter.md_to_html(content)
        
        ai_detection = None
        ai_score = None
        
        if run_ai_validation:
            text_content = markdown_converter.md_to_text(content)
            
            logger.info(f"Running AI validation on {tab_name} content for college ID: {college_id}")
            ai_validation_service = AIValidationService()
            ai_validation_result = await ai_validation_service.detect_ai_from_text(text_content)
            
            ai_detection = ai_validation_result
            ai_score = ai_validation_result.get('overall_score')
            
            logger.info(f"AI validation completed for college ID: {college_id} - Score: {ai_score}")

        result = ContentResponse(
            content=content,
            html_content=html_content,
            college_name=college_name,
            metadata={"ai_detection": ai_detection} if ai_detection else {}
        )
        
        await _persist_generated_result(result, college_id, tab_name, run_ai_validation)
        
        return str(uuid.uuid4())
        
    except Exception as e:
        logger.error(f"Error saving content to database: {e}")
        return None


async def run_ai_validation(content: str, college_id: int, tab_name: str) -> None:
    """Run AI validation on content (legacy function for compatibility)."""
    await save_content_to_database(content, college_id, tab_name, run_ai_validation=True)


async def main() -> int:
    """Main function."""
    parser = argparse.ArgumentParser(description="Simple AI Content Generator")
    parser.add_argument("--college-id", type=int, required=True, help="College ID")
    parser.add_argument("--type", choices=["overview", "fees", "reviews", "courses", "campus", "overview_short"], default="overview", 
                        help="Content type to generate")
    parser.add_argument("--api-key", help="Google API key")
    parser.add_argument("--ai-validation", action="store_true", help="Run AI validation")
    parser.add_argument("--save-to-db", action="store_true", help="Save content to database")
    parser.add_argument("--save-to-tabs", action="store_true", help="Save content to fmc_content_tabs table")
    
    args = parser.parse_args()
    setup_logging()
    
    api_key = args.api_key or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("Google API key is required. Set GOOGLE_API_KEY environment variable or use --api-key")
        return 1
    
    config = GeneratorConfig(api_key=api_key)
    logger.info(f"Generating {args.type} content for college ID: {args.college_id}")
    
    result: Optional[str] = None
    
    try:
        if args.type  == "overview":
            result = await generate_overview(config, args.college_id)
        
        if args.type == "fees":
            fees_content = await generate_fees(config, args.college_id)
            result = fees_content['overview']
        
        if args.type == "reviews":
            reviews_content = await generate_reviews(config, args.college_id)
            result = reviews_content
        
        if args.type == "courses":
            courses_content = await generate_courses(config, args.college_id)
            result = courses_content

        if args.type == "campus":
            campus_content = await generate_campus(config, args.college_id)
            result = campus_content

        if args.type == "overview_short":
            overview_short_content = await generate_overview_short(config, args.college_id)
            result = overview_short_content
 
        print("--------------------------------")
        print(result)
        print("--------------------------------")
 
        if args.ai_validation and result:
            await run_ai_validation(result, args.college_id, args.type)
            
    except Exception as e:
        logger.error(f"Content generation failed: {e}")
        return 1

    logger.info("Content generation completed!")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
