#!/usr/bin/env python3
"""
Batch College Content Generation Script
Process multiple colleges in sequence or parallel.
"""

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import List

# Add the project root to sys.path
_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from run_all_tabs import process_all_tabs  # noqa: E402
from src.models.generator import GeneratorConfig  # noqa: E402
from src.utils.logging_config import get_logger  # noqa: E402

logger = get_logger(__name__)


def setup_logging() -> None:
    """Setup simple logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


async def process_college_batch(
    college_ids: List[int], 
    config: GeneratorConfig, 
    run_ai_validation: bool = True,
    parallel: bool = False
) -> dict:
    """Process a batch of colleges either sequentially or in parallel."""
    
    if parallel:
        logger.info(f"🚀 Processing {len(college_ids)} colleges in parallel...")
        tasks = [
            process_all_tabs(college_id, config, run_ai_validation) 
            for college_id in college_ids
        ]
        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert results to dictionary
        batch_results = {}
        for i, college_id in enumerate(college_ids):
            if isinstance(results_list[i], Exception):
                logger.error(f"❌ College {college_id} failed: {results_list[i]}")
                batch_results[college_id] = {"error": str(results_list[i])}
            else:
                batch_results[college_id] = results_list[i]
    else:
        logger.info(f"🚀 Processing {len(college_ids)} colleges sequentially...")
        batch_results = {}
        
        for i, college_id in enumerate(college_ids, 1):
            logger.info(f"📋 Processing college {i}/{len(college_ids)}: {college_id}")
            try:
                results = await process_all_tabs(college_id, config, run_ai_validation)
                batch_results[college_id] = results
                logger.info(f"✅ College {college_id} completed")
            except Exception as e:
                logger.error(f"❌ College {college_id} failed: {e}")
                batch_results[college_id] = {"error": str(e)}
    
    return batch_results


def print_batch_summary(batch_results: dict) -> None:
    """Print a summary of batch processing results."""
    total_colleges = len(batch_results)
    successful_colleges = 0
    partial_colleges = 0
    failed_colleges = 0
    
    logger.info("📊 BATCH PROCESSING SUMMARY")
    logger.info("=" * 50)
    
    for college_id, results in batch_results.items():
        if "error" in results:
            logger.info(f"❌ College {college_id}: FAILED - {results['error']}")
            failed_colleges += 1
        else:
            successful_tabs = sum(1 for success in results.values() if success)
            total_tabs = len(results)
            
            if successful_tabs == total_tabs:
                logger.info(f"✅ College {college_id}: SUCCESS ({successful_tabs}/{total_tabs} tabs)")
                successful_colleges += 1
            elif successful_tabs > 0:
                logger.info(f"⚠️ College {college_id}: PARTIAL ({successful_tabs}/{total_tabs} tabs)")
                partial_colleges += 1
            else:
                logger.info(f"❌ College {college_id}: FAILED (0/{total_tabs} tabs)")
                failed_colleges += 1
    
    logger.info("=" * 50)
    logger.info("📈 FINAL STATISTICS:")
    logger.info(f"   🎯 Total Colleges: {total_colleges}")
    logger.info(f"   ✅ Successful: {successful_colleges}")
    logger.info(f"   ⚠️ Partial: {partial_colleges}")
    logger.info(f"   ❌ Failed: {failed_colleges}")
    logger.info(f"   📊 Success Rate: {(successful_colleges/total_colleges)*100:.1f}%")


async def main() -> int:
    """Main function."""
    parser = argparse.ArgumentParser(description="Batch process multiple colleges")
    parser.add_argument("--college-ids", type=str, required=True, 
                       help="Comma-separated list of college IDs (e.g., '1,4,5,6')")
    parser.add_argument("--api-key", help="Google API key")
    parser.add_argument("--no-ai-validation", action="store_true", help="Skip AI validation")
    parser.add_argument("--parallel", action="store_true", help="Process colleges in parallel")
    parser.add_argument("--max-concurrent", type=int, default=3, 
                       help="Maximum concurrent colleges when using parallel processing")
    
    args = parser.parse_args()
    setup_logging()
    
    # Parse college IDs
    try:
        college_ids = [int(x.strip()) for x in args.college_ids.split(",")]
        logger.info(f"📋 College IDs to process: {college_ids}")
    except ValueError as e:
        logger.error(f"❌ Invalid college IDs format: {e}")
        return 1
    
    api_key = args.api_key or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("❌ Google API key is required. Set GOOGLE_API_KEY environment variable or use --api-key")
        return 1
    
    config = GeneratorConfig(api_key=api_key)
    run_ai_validation = not args.no_ai_validation
    
    logger.info(f"🚀 Batch Processing Configuration:")
    logger.info(f"   📊 Colleges: {len(college_ids)}")
    logger.info(f"   🤖 AI Validation: {'Enabled' if run_ai_validation else 'Disabled'}")
    logger.info(f"   ⚡ Processing Mode: {'Parallel' if args.parallel else 'Sequential'}")
    if args.parallel:
        logger.info(f"   🔄 Max Concurrent: {args.max_concurrent}")
    
    try:
        if args.parallel and len(college_ids) > args.max_concurrent:
            # Process in batches if there are too many colleges
            logger.info(f"🔄 Processing in batches of {args.max_concurrent}...")
            batch_results = {}
            
            for i in range(0, len(college_ids), args.max_concurrent):
                batch = college_ids[i:i + args.max_concurrent]
                logger.info(f"📦 Processing batch {i//args.max_concurrent + 1}: {batch}")
                
                batch_result = await process_college_batch(batch, config, run_ai_validation, parallel=True)
                batch_results.update(batch_result)
        else:
            batch_results = await process_college_batch(college_ids, config, run_ai_validation, args.parallel)
        
        print_batch_summary(batch_results)
        
        # Determine exit code based on results
        successful = sum(1 for results in batch_results.values() 
                        if "error" not in results and all(results.values()))
        total = len(batch_results)
        
        if successful == total:
            logger.info("🎉 All colleges processed successfully!")
            return 0
        elif successful > 0:
            logger.warning(f"⚠️ Partial success: {successful}/{total} colleges completed successfully")
            return 2
        else:
            logger.error("❌ All colleges failed to process")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Batch processing failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
