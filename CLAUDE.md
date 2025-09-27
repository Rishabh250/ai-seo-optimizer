# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI SEO Optimizer that generates educational content for colleges using Google's Generative AI. The system generates six types of content: overviews, fees, reviews, courses, campus, and overview_short for educational institutions using data from a PostgreSQL database.

## Commands

### Development Commands
```bash
# Install dependencies using uv (preferred) or pip
uv pip install -r requirements.txt
# OR
pip install -r requirements.txt

# Run the main application
python main.py --college-id 4 --type overview

# Generate specific content types
python main.py --college-id 4 --type overview
python main.py --college-id 4 --type fees
python main.py --college-id 4 --type reviews
python main.py --college-id 4 --type courses
python main.py --college-id 4 --type campus
python main.py --college-id 4 --type overview_short

# Run with AI validation
python main.py --college-id 4 --ai-validation

# Save content to database
python main.py --college-id 4 --save-to-db
python main.py --college-id 4 --save-to-tabs

# Override API key
python main.py --college-id 4 --api-key "your_key_here"

# Bulk generation commands
# Generate overviews for all colleges
python generate_all_overviews.py --api-key "your_key_here"

# Generate with database saving
python generate_all_overviews.py --save-to-db

# Generate with AI validation
python generate_all_overviews.py --ai-validation --gptzero-api-key "your_key"

# Generate with both database saving and AI validation
python generate_all_overviews.py --save-to-db --ai-validation

# Process specific colleges
python generate_all_overviews.py --college-ids "1,4,5,10"

# Process with limits and offsets
python generate_all_overviews.py --limit 50 --offset 100

# Dry run to see what would be processed
python generate_all_overviews.py --dry-run --limit 10

# Enhanced script with start-from capability and AI humanization retries
# Start processing from a specific college ID with humanization retries
python generate_overviews_from.py --start-from 100 --limit 50 --save-to-db --ai-validation

# Process with custom retry attempts for AI scores >90%
python generate_overviews_from.py --start-from 1 --limit 10 --save-to-db --ai-validation --max-retries 3

# Process a range of colleges with humanization
python generate_overviews_from.py --start-from 100 --end-at 200 --save-to-db --ai-validation --max-retries 2

# Start from college ID 50 and process next 25 colleges
python generate_overviews_from.py --start-from 50 --limit 25 --delay 1.5

# Dry run to see what would be processed from a specific point
python generate_overviews_from.py --start-from 100 --limit 10 --dry-run

# Overview Short generation script with start-from capability and AI humanization retries
# Start processing overview_short from a specific college ID with humanization
python generate_overview_short_from.py --start-from 1 --limit 10 --save-to-db --ai-validation

# Process overview_short with custom retry attempts for AI scores >90%
python generate_overview_short_from.py --start-from 1 --limit 10 --save-to-db --ai-validation --max-retries 3

# Process overview_short for a range of colleges with humanization
python generate_overview_short_from.py --start-from 100 --end-at 200 --save-to-db --ai-validation --max-retries 2

# Start from college ID 50 and process next 25 overview_short content
python generate_overview_short_from.py --start-from 50 --limit 25 --delay 1.5

# Dry run to see what would be processed for overview_short
python generate_overview_short_from.py --start-from 100 --limit 10 --dry-run
```

### Batch Processing Commands
```bash
# Process multiple colleges sequentially
python batch_process.py --college-ids "1,4,5,6"

# Process multiple colleges in parallel
python batch_process.py --college-ids "1,4,5,6" --parallel

# Control parallel processing with max concurrent limit
python batch_process.py --college-ids "1,4,5,6" --parallel --max-concurrent 3

# Skip AI validation for faster processing
python batch_process.py --college-ids "1,4,5,6" --no-ai-validation
```

### All Tabs Processing
```bash
# Generate all content types for a single college
python run_all_tabs.py --college-id 4

# Generate all tabs with AI validation
python run_all_tabs.py --college-id 4 --ai-validation
```

### Environment Setup
```bash
# Copy environment template
cp .env.example .env

# Set required environment variables
export GOOGLE_API_KEY="your_google_api_key"
export DB_HOST="localhost"
export DB_NAME="college_db"
export DB_USER="postgres"
export DB_PASSWORD="your_db_password"
```

## Architecture

### Core Structure
- **main.py**: Entry point with CLI interface and content generation orchestration
- **batch_process.py**: Batch processing script for multiple colleges with parallel/sequential options
- **run_all_tabs.py**: Generates all content types (tabs) for a single college
- **src/core/**: Content generators for different content types (overview, fees, reviews, courses, campus, overview_short)
- **src/services/**: Business logic services including AI validation, content analysis, and markdown conversion
- **src/database/**: Database services for accessing college, fees, reviews, course, and campus data
- **src/models/**: Data models and configuration classes
- **src/utils/**: Utilities including prompts, exceptions, and logging

### Key Components

**Content Generators**: Each content type has its own generator class that handles the AI generation workflow:
- `CollegeOverviewGenerator`: Generates comprehensive college overviews
- `CollegeOverviewShortGenerator`: Creates short overview summaries
- `FeesContentGenerator`: Creates detailed fees information
- `ReviewsContentGenerator`: Produces student review content
- `CourseContentGenerator`: Generates course catalog information (async)
- `CampusContentGenerator`: Generates campus information and facilities

**Database Layer**: Service classes handle data retrieval from PostgreSQL:
- Expected tables: `fmc_summary` (college info), `fmc_degree_fees` (fees data), `fmc_reviews` (reviews), course-related tables
- All services use connection pooling via `DatabaseManager`
- Content persistence through `ContentAnalysisService` with advanced AI score comparison

**AI Integration**: Uses LangChain with Google Generative AI:
- Default model: `gemini-2.5-flash`
- Temperature: 0.3 (configurable via `GeneratorConfig`)
- Structured prompts in `src/utils/prompts/`

**Content Processing Pipeline**: Advanced content handling with multiple persistence strategies:
- AI validation using `AIValidationService` with GPTZero integration
- Markdown-to-HTML conversion via `MarkdownConverterService`
- Smart content upserting based on AI detection scores
- Support for both regular and short content types

### Key Patterns

**Configuration**: Uses dataclasses for configuration management (`GeneratorConfig`, `PromptVariables`)

**Error Handling**: Custom exceptions in `src/utils/exceptions.py` for domain-specific error cases

**Async Support**: Course generation, AI validation, and content persistence use async/await patterns

**Content Validation**: Optional AI-generated content detection via `AIValidationService` with score-based persistence decisions

**Markdown Processing**: Convert between markdown, HTML, and plain text using `MarkdownConverterService`

**Batch Processing**: Support for processing multiple colleges with configurable parallelism and error handling

## Dependencies

The project uses Python 3.13+ and includes:
- **langchain**: AI framework for LLM integration (>=0.3.0,<0.4.0)
- **langchain-google-genai**: Google AI integration (>=2.0.0,<3.0.0)
- **google-generativeai**: Direct Google AI SDK (>=0.7.0,<0.8.0)
- **psycopg2-binary**: PostgreSQL database connectivity (>=2.9.0)
- **python-dotenv**: Environment variable management (>=1.0.0)
- **markdown-it-py**: Markdown processing (>=3.0.0,<4.0.0)

## Database Requirements

Ensure PostgreSQL is running with the expected schema:
- College information in `fmc_summary` table
- Fees data in `fmc_degree_fees` table
- Reviews data in `fmc_reviews` table
- Course data in appropriate tables (structure varies by generator)
- Content analysis tracking in `content_analysis` table
- Tab content storage in `fmc_content_tabs` and short content variants