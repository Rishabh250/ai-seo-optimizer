# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI SEO Optimizer that generates educational content for colleges using Google's Generative AI. The system generates four types of content: overviews, fees, reviews, and courses for educational institutions using data from a PostgreSQL database.

## Commands

### Development Commands
```bash
# Install dependencies using uv (preferred) or pip
uv pip install -r requirements.txt
# OR
pip install -r requirements.txt

# Run the main application
python main.py --college-id 4 --type all

# Generate specific content types
python main.py --college-id 4 --type overview
python main.py --college-id 4 --type fees
python main.py --college-id 4 --type reviews
python main.py --college-id 4 --type courses

# Run with AI validation
python main.py --college-id 4 --ai-validation

# Override API key
python main.py --college-id 4 --api-key "your_key_here"
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
- **src/core/**: Content generators for different content types (overview, fees, reviews, courses)
- **src/services/**: Business logic services including AI validation and markdown conversion
- **src/database/**: Database services for accessing college, fees, reviews, and course data
- **src/models/**: Data models and configuration classes
- **src/utils/**: Utilities including prompts, exceptions, and logging

### Key Components

**Content Generators**: Each content type has its own generator class that handles the AI generation workflow:
- `CollegeOverviewGenerator`: Generates comprehensive college overviews
- `FeesContentGenerator`: Creates detailed fees information
- `ReviewsContentGenerator`: Produces student review content
- `CourseContentGenerator`: Generates course catalog information

**Database Layer**: Service classes handle data retrieval from PostgreSQL:
- Expected tables: `fmc_summary` (college info), `fmc_degree_fees` (fees data), `fmc_reviews` (reviews), course-related tables
- All services use connection pooling via `DatabaseManager`

**AI Integration**: Uses LangChain with Google Generative AI:
- Default model: `gemini-2.5-flash`
- Temperature: 0.3 (configurable via `GeneratorConfig`)
- Structured prompts in `src/utils/prompts/`

### Key Patterns

**Configuration**: Uses dataclasses for configuration management (`GeneratorConfig`, `PromptVariables`)

**Error Handling**: Custom exceptions in `src/utils/exceptions.py` for domain-specific error cases

**Async Support**: Course generation and AI validation use async/await patterns

**Content Validation**: Optional AI-generated content detection via `AIValidationService`

**Markdown Processing**: Convert between markdown and plain text using `MarkdownConverterService`

## Dependencies

The project uses Python 3.13+ and includes:
- **langchain**: AI framework for LLM integration
- **langchain-google-genai**: Google AI integration
- **google-generativeai**: Direct Google AI SDK
- **psycopg2-binary**: PostgreSQL database connectivity
- **python-dotenv**: Environment variable management
- **markdown-related**: Markdown processing libraries

## Database Requirements

Ensure PostgreSQL is running with the expected schema:
- College information in `fmc_summary` table
- Fees data in `fmc_degree_fees` table
- Reviews data in `fmc_reviews` table
- Course data in appropriate tables (structure varies by generator)