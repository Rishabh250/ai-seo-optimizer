#!/usr/bin/env python3
"""
Simple AI Content Generator - Clean and minimal implementation
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add the project root to sys.path
_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

from src.core.fees_generator import FeesContentGenerator  # noqa: E402
from src.core.overview_generator import CollegeOverviewGenerator  # noqa: E402
from src.models.generator import GeneratorConfig  # noqa: E402


def setup_logging():
    """Setup simple logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def main():
    """Simple main function."""
    parser = argparse.ArgumentParser(description="Simple AI Content Generator")
    parser.add_argument("--college-id", type=int, required=True, help="College ID")
    parser.add_argument("--type", choices=["overview", "fees", "both"], default="both", 
                       help="Content type to generate")
    parser.add_argument("--api-key", help="Google API key")
    
    args = parser.parse_args()
    
    setup_logging()
    
    api_key = args.api_key or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ Error: Google API key is required. Set GOOGLE_API_KEY environment variable or use --api-key")
        return 1
    
    config = GeneratorConfig(api_key=api_key)
    
    print(f"🚀 Generating {args.type} content for college ID: {args.college_id}")
    
    try:
        if args.type == "overview":
            generator = CollegeOverviewGenerator(config)
            overview = generator.generate_by_college_id(args.college_id)
            
            print("\n" + "="*60)
            print("📄 OVERVIEW CONTENT")
            print("="*60)
            print(overview)
        
        if args.type == "fees":
            generator = FeesContentGenerator(config)
            fees_content = generator.generate_fees_by_college_id(args.college_id)
            
            print("\n" + "="*60)
            print("💰 FEES CONTENT")
            print("="*60)
            
            if isinstance(fees_content, dict):
                for degree, content in fees_content.items():
                    print(f"\n--- {degree.upper()} ---")
                    print(content)
            else:
                print(fees_content)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    print("\n✅ Content generation completed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())

