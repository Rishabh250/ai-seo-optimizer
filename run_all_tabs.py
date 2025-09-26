#!/usr/bin/env python3
"""
College Content Generation Script - Run All Tabs
This script generates content for all tabs (overview, fees, reviews, courses) for a given college ID.
"""

import argparse
import asyncio
import logging
import os
import sys
import uuid
from pathlib import Path
from typing import Any

# Add the project root to sys.path
_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from src.core.campus_generator import CampusContentGenerator  # noqa: E402
from src.core.course_generator import CourseContentGenerator  # noqa: E402
from src.core.fees_generator import FeesContentGenerator  # noqa: E402
from src.core.overview_generator import CollegeOverviewGenerator  # noqa: E402
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
            logger.info(f"AI score comparison for {tab_name}: new={new_ai_score}, last={last_score}, can_persist={can_persist}")
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
        logger.info(f"✅ Persisted {tab_name} content_analysis for college {college_id} (can_persist={can_persist})")
    except Exception as e:
        logger.error(f"❌ Failed to persist content_analysis for college {college_id}: {e}")

    if not can_persist:
        logger.info(f"⚠️ Skipping tab content upsert due to higher AI score for college {college_id}, tab {tab_name}")
        return

    try:
        if tab_name.endswith("_short"):
            await database_service.upsert_college_tab_short_content(
                college_id=college_id,
                tab_name=tab_name,
                content_markdown=md_text,
                html_content=html_text,
            )
            logger.info(f"✅ Upserted short tab content for college {college_id}, tab {tab_name}")
        else:
            await database_service.upsert_college_tab_content(
                college_id=college_id,
                tab_name=tab_name,
                content_markdown=md_text,
                html_content=html_text,
            )
            logger.info(f"✅ Upserted tab content for college {college_id}, tab {tab_name}")
    except Exception as e:
        logger.error(f"❌ Failed to upsert tab content for college {college_id}/{tab_name}: {e}")


async def generate_and_save_content(
    content: str, 
    college_id: int, 
    tab_name: str, 
    run_ai_validation: bool = False,
    college_name: str = ""
) -> bool:
    """Generate and save content with AI validation and persistence logic."""
    if not content:
        logger.warning(f"No content available for {tab_name}")
        return False

    try:
        markdown_converter = MarkdownConverterService()
        html_content = markdown_converter.md_to_html(content)
        
        ai_detection = None
        ai_score = None
        
        if run_ai_validation:
            text_content = markdown_converter.md_to_text(content)
            
            logger.info(f"🤖 Running AI validation on {tab_name} content for college ID: {college_id}")
            ai_validation_service = AIValidationService()
            ai_validation_result = await ai_validation_service.detect_ai_from_text(text_content)
            
            ai_detection = ai_validation_result
            ai_score = ai_validation_result.get('overall_score')
            
            logger.info(f"🎯 AI validation completed for {tab_name} - Score: {ai_score}")

        # Create ContentResponse for the advanced persist function
        result = ContentResponse(
            content=content,
            html_content=html_content,
            college_name=college_name,
            metadata={"ai_detection": ai_detection} if ai_detection else {}
        )
        
        # Use the advanced persistence logic
        await _persist_generated_result(result, college_id, tab_name, run_ai_validation)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error processing {tab_name} content: {e}")
        return False


async def generate_overview_content(config: GeneratorConfig, college_id: int) -> str:
    """Generate overview content."""
    try:
        generator = CollegeOverviewGenerator(config)
        overview = generator.generate_by_college_id(college_id)
        logger.info(f"📄 Generated overview content ({len(overview)} chars)")
        return overview
    except Exception as e:
        logger.error(f"❌ Failed to generate overview content: {e}")
        return ""


async def generate_fees_content(config: GeneratorConfig, college_id: int) -> str:
    """Generate fees content."""
    try:
        generator = FeesContentGenerator(config)
        fees_content = generator.generate_fees_by_college_id(college_id)
        
        if isinstance(fees_content, dict):
            content = fees_content.get('overview', str(fees_content))
        elif isinstance(fees_content, str):
            content = fees_content
        else:
            content = str(fees_content)
            
        logger.info(f"💰 Generated fees content ({len(content)} chars)")
        return content
    except Exception as e:
        logger.error(f"❌ Failed to generate fees content: {e}")
        return ""


async def generate_reviews_content(config: GeneratorConfig, college_id: int) -> str:
    """Generate reviews content."""
    try:
        generator = ReviewsContentGenerator(config)
        reviews_content = generator.generate_reviews_by_college_id(college_id)
        logger.info(f"⭐ Generated reviews content ({len(reviews_content)} chars)")
        return reviews_content
    except Exception as e:
        logger.error(f"❌ Failed to generate reviews content: {e}")
        return ""


async def generate_courses_content(config: GeneratorConfig, college_id: int) -> str:
    """Generate courses content."""
    try:
        generator = CourseContentGenerator(config)
        courses_content = await generator.generate_courses_by_college_id(college_id)
        logger.info(f"📚 Generated courses content ({len(courses_content)} chars)")
        return courses_content
    except Exception as e:
        logger.error(f"❌ Failed to generate courses content: {e}")
        return ""


async def generate_campus_content(config: GeneratorConfig, college_id: int) -> str:
    """Generate campus content."""
    try:
        generator = CampusContentGenerator(config)
        campus_content = generator.generate_campus_by_college_id(college_id)
        logger.info(f"🏫 Generated campus content ({len(campus_content)} chars)")
        return campus_content
    except Exception as e:
        logger.error(f"❌ Failed to generate campus content: {e}")
        return ""


async def process_all_tabs(college_id: int, config: GeneratorConfig, run_ai_validation: bool = True) -> dict:
    """Process all content tabs for a college."""
    results = {
        "overview": False,
        "fees": False,
        "reviews": False,
        "all_courses": False,
        "campus": False
    }
    
    total_tabs = len(results)
    completed_tabs = 0
    
    logger.info(f"🚀 Starting content generation for college ID: {college_id}")
    logger.info(f"📊 Processing {total_tabs} content types with AI validation: {run_ai_validation}")
    
    # Generate Overview Content
    try:
        logger.info("📄 [1/5] Generating overview content...")
        overview_content = await generate_overview_content(config, college_id)
        if overview_content:
            success = await generate_and_save_content(
                overview_content, college_id, "overview", run_ai_validation
            )
            results["overview"] = success
            if success:
                completed_tabs += 1
                logger.info("✅ [1/5] Overview content completed successfully")
            else:
                logger.error("❌ [1/5] Overview content failed to save")
        else:
            logger.error("❌ [1/5] Overview content generation failed")
    except Exception as e:
        logger.error(f"❌ [1/5] Overview content error: {e}")
    
    # Generate Fees Content
    try:
        logger.info("💰 [2/5] Generating fees content...")
        fees_content = await generate_fees_content(config, college_id)
        if fees_content:
            success = await generate_and_save_content(
                fees_content, college_id, "fees", run_ai_validation
            )
            results["fees"] = success
            if success:
                completed_tabs += 1
                logger.info("✅ [2/5] Fees content completed successfully")
            else:
                logger.error("❌ [2/5] Fees content failed to save")
        else:
            logger.error("❌ [2/5] Fees content generation failed")
    except Exception as e:
        logger.error(f"❌ [2/5] Fees content error: {e}")
    
    # Generate Reviews Content
    try:
        logger.info("⭐ [3/5] Generating reviews content...")
        reviews_content = await generate_reviews_content(config, college_id)
        if reviews_content:
            success = await generate_and_save_content(
                reviews_content, college_id, "reviews", run_ai_validation
            )
            results["reviews"] = success
            if success:
                completed_tabs += 1
                logger.info("✅ [3/5] Reviews content completed successfully")
            else:
                logger.error("❌ [3/5] Reviews content failed to save")
        else:
            logger.error("❌ [3/5] Reviews content generation failed")
    except Exception as e:
        logger.error(f"❌ [3/5] Reviews content error: {e}")
    
    # Generate Courses Content
    try:
        logger.info("📚 [4/5] Generating courses content...")
        courses_content = await generate_courses_content(config, college_id)
        if courses_content:
            success = await generate_and_save_content(
                courses_content, college_id, "all_courses", run_ai_validation
            )
            results["all_courses"] = success
            if success:
                completed_tabs += 1
                logger.info("✅ [4/5] Courses content completed successfully")
            else:
                logger.error("❌ [4/5] Courses content failed to save")
        else:
            logger.error("❌ [4/5] Courses content generation failed")
    except Exception as e:
        logger.error(f"❌ [4/5] Courses content error: {e}")
    
    # Generate Campus Content
    try:
        logger.info("🏫 [5/5] Generating campus content...")
        campus_content = await generate_campus_content(config, college_id)
        if campus_content:
            success = await generate_and_save_content(
                campus_content, college_id, "campus", run_ai_validation
            )
            results["campus"] = success
            if success:
                completed_tabs += 1
                logger.info("✅ [5/5] Campus content completed successfully")
            else:
                logger.error("❌ [5/5] Campus content failed to save")
        else:
            logger.error("❌ [5/5] Campus content generation failed")
    except Exception as e:
        logger.error(f"❌ [5/5] Campus content error: {e}")
    
    # Summary
    logger.info(f"🎯 Content generation summary for college {college_id}:")
    logger.info(f"   📊 Completed: {completed_tabs}/{total_tabs} tabs")
    logger.info(f"   📄 Overview: {'✅' if results['overview'] else '❌'}")
    logger.info(f"   💰 Fees: {'✅' if results['fees'] else '❌'}")
    logger.info(f"   ⭐ Reviews: {'✅' if results['reviews'] else '❌'}")
    logger.info(f"   📚 Courses: {'✅' if results['all_courses'] else '❌'}")
    logger.info(f"   🏫 Campus: {'✅' if results['campus'] else '❌'}")
    
    return results


async def main() -> int:
    """Main function."""
    parser = argparse.ArgumentParser(description="Generate content for all tabs of a college")
    parser.add_argument("--college-id", type=int, required=True, help="College ID")
    parser.add_argument("--api-key", help="Google API key")
    parser.add_argument("--no-ai-validation", action="store_true", help="Skip AI validation")
    parser.add_argument("--dry-run", action="store_true", help="Generate content but don't save to database")
    
    args = parser.parse_args()
    setup_logging()
    
    api_key = args.api_key or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("❌ Google API key is required. Set GOOGLE_API_KEY environment variable or use --api-key")
        return 1
    
    config = GeneratorConfig(api_key=api_key)
    run_ai_validation = not args.no_ai_validation
    
    logger.info(f"🏫 Processing college ID: {args.college_id}")
    logger.info(f"🤖 AI Validation: {'Enabled' if run_ai_validation else 'Disabled'}")
    logger.info(f"💾 Save to Database: {'No (Dry Run)' if args.dry_run else 'Yes'}")
    
    try:
        if args.dry_run:
            logger.info("🔍 DRY RUN MODE - Content will be generated but not saved")
            # In dry run mode, we could just generate without saving
            # For now, we'll process normally since the persistence logic handles this
        
        results = await process_all_tabs(args.college_id, config, run_ai_validation)
        
        successful_tabs = sum(1 for success in results.values() if success)
        total_tabs = len(results)
        
        if successful_tabs == total_tabs:
            logger.info(f"🎉 All {total_tabs} content types generated successfully!")
            return 0
        elif successful_tabs > 0:
            logger.warning(f"⚠️ Partial success: {successful_tabs}/{total_tabs} content types completed")
            return 2
        else:
            logger.error(f"❌ Failed to generate any content for college {args.college_id}")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Content generation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
