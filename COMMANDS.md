# AI SEO Optimizer - Command Reference

This file contains all available commands for the AI SEO Optimizer system.

## Basic Content Generation Commands

### Single College Content Generation

```bash
# Generate overview content
python3 main.py --college-id 4 --type overview

# Generate fees content
python3 main.py --college-id 4 --type fees

# Generate reviews content
python3 main.py --college-id 4 --type reviews

# Generate courses content
python3 main.py --college-id 4 --type courses

# Generate campus content
python3 main.py --college-id 4 --type campus

# Generate short overview content
python3 main.py --college-id 4 --type overview_short

# Generate with AI validation
python3 main.py --college-id 4 --ai-validation

# Save content to database
python3 main.py --college-id 4 --save-to-db
python3 main.py --college-id 4 --save-to-tabs

# Override API key
python3 main.py --college-id 4 --api-key "your_key_here"
```

## Enhanced Bulk Generation Scripts (with AI Humanization)

### Overview Generation (Full College Overviews)

```bash
# Basic overview generation for all colleges
python3 generate_overviews_from.py --api-key "your_key_here"

# Generate with database saving
python3 generate_overviews_from.py --save-to-db

# Generate with AI validation
python3 generate_overviews_from.py --ai-validation --gptzero-api-key "your_key"

# Generate with both database saving and AI validation
python3 generate_overviews_from.py --save-to-db --ai-validation

# Process specific colleges
python3 generate_overviews_from.py --college-ids "1,4,5,10"

# Process with limits and offsets
python3 generate_overviews_from.py --limit 50 --offset 100

# Dry run to see what would be processed
python3 generate_overviews_from.py --dry-run --limit 10

# Start processing from a specific college ID with humanization retries
python3 generate_overviews_from.py --start-from 100 --limit 50 --save-to-db --ai-validation

# Process with custom retry attempts for AI scores >90%
python3 generate_overviews_from.py --start-from 1 --limit 10 --save-to-db --ai-validation --max-retries 3

# Process a range of colleges with humanization
python3 generate_overviews_from.py --start-from 100 --end-at 200 --save-to-db --ai-validation --max-retries 2

# Start from college ID 50 and process next 25 colleges
python3 generate_overviews_from.py --start-from 50 --limit 25 --delay 1.5

# Dry run to see what would be processed from a specific point
python3 generate_overviews_from.py --start-from 100 --limit 10 --dry-run
```

### Overview Short Generation (Short College Summaries)

```bash
# Start processing overview_short from a specific college ID with humanization
python3 generate_overview_short_from.py --start-from 1 --limit 10 --save-to-db --ai-validation

# Process overview_short with custom retry attempts for AI scores >90%
python3 generate_overview_short_from.py --start-from 1 --limit 10 --save-to-db --ai-validation --max-retries 3

# Process overview_short for a range of colleges with humanization
python3 generate_overview_short_from.py --start-from 100 --end-at 200 --save-to-db --ai-validation --max-retries 2

# Start from college ID 50 and process next 25 overview_short content
python3 generate_overview_short_from.py --start-from 50 --limit 25 --delay 1.5

# Dry run to see what would be processed for overview_short
python3 generate_overview_short_from.py --start-from 100 --limit 10 --dry-run

# Basic overview_short generation with all features
python3 generate_overview_short_from.py --start-from 1 --limit 100 --save-to-db --ai-validation --max-retries 3
```

### Courses Generation (Complete Course Information)

```bash
# Start processing courses from a specific college ID with humanization
python3 generate_courses_from.py --start-from 1 --limit 10 --save-to-db --ai-validation

# Process courses with custom retry attempts for AI scores >90%
python3 generate_courses_from.py --start-from 1 --limit 10 --save-to-db --ai-validation --max-retries 3

# Process courses for a range of colleges with humanization
python3 generate_courses_from.py --start-from 100 --end-at 200 --save-to-db --ai-validation --max-retries 2

# Start from college ID 50 and process next 25 courses content
python3 generate_courses_from.py --start-from 50 --limit 25 --delay 1.5

# Dry run to see what would be processed for courses
python3 generate_courses_from.py --start-from 100 --limit 10 --dry-run

# Basic courses generation with all features
python3 generate_courses_from.py --start-from 1 --limit 100 --save-to-db --ai-validation --max-retries 3
```

### Course Short Generation (Short Course Summaries)

```bash
# Start processing course_short from a specific college ID with humanization
python3 generate_course_short_from.py --start-from 1 --limit 10 --save-to-db --ai-validation

# Process course_short with custom retry attempts for AI scores >90%
python3 generate_course_short_from.py --start-from 1 --limit 10 --save-to-db --ai-validation --max-retries 3

# Process course_short for a range of colleges with humanization
python3 generate_course_short_from.py --start-from 100 --end-at 200 --save-to-db --ai-validation --max-retries 2

# Start from college ID 50 and process next 25 course_short content
python3 generate_course_short_from.py --start-from 50 --limit 25 --delay 1.5

# Dry run to see what would be processed for course_short
python3 generate_course_short_from.py --start-from 100 --limit 10 --dry-run

# Basic course_short generation with all features
python3 generate_course_short_from.py --start-from 1 --limit 100 --save-to-db --ai-validation --max-retries 3
```

## Legacy Bulk Generation Commands

### Basic Bulk Generation (Legacy)

```bash
# Generate overviews for all colleges
python3 generate_all_overviews.py --api-key "your_key_here"

# Generate with database saving
python3 generate_all_overviews.py --save-to-db

# Generate with AI validation
python3 generate_all_overviews.py --ai-validation --gptzero-api-key "your_key"

# Generate with both database saving and AI validation
python3 generate_all_overviews.py --save-to-db --ai-validation

# Process specific colleges
python3 generate_all_overviews.py --college-ids "1,4,5,10"

# Process with limits and offsets
python3 generate_all_overviews.py --limit 50 --offset 100

# Dry run to see what would be processed
python3 generate_all_overviews.py --dry-run --limit 10
```

## Batch Processing Commands

### Sequential and Parallel Processing

```bash
# Process multiple colleges sequentially
python3 batch_process.py --college-ids "1,4,5,6"

# Process multiple colleges in parallel
python3 batch_process.py --college-ids "1,4,5,6" --parallel

# Control parallel processing with max concurrent limit
python3 batch_process.py --college-ids "1,4,5,6" --parallel --max-concurrent 3

# Skip AI validation for faster processing
python3 batch_process.py --college-ids "1,4,5,6" --no-ai-validation
```

### All Tabs Processing

```bash
# Generate all content types for a single college
python3 run_all_tabs.py --college-id 4

# Generate all tabs with AI validation
python3 run_all_tabs.py --college-id 4 --ai-validation
```

## Environment Setup Commands

### Initial Setup

```bash
# Install dependencies using uv (preferred)
uv pip install -r requirements.txt

# Install dependencies using pip
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Set required environment variables
export GOOGLE_API_KEY="your_google_api_key"
export DB_HOST="localhost"
export DB_NAME="college_db"
export DB_USER="postgres"
export DB_PASSWORD="your_db_password"
```

## Common Command Patterns

### Production-Ready Commands

```bash
# Full overview generation with all features
python3 generate_overviews_from.py --start-from 1 --limit 1000 --save-to-db --ai-validation --max-retries 3 --delay 2.0

# Full overview_short generation with all features
python3 generate_overview_short_from.py --start-from 1 --limit 1000 --save-to-db --ai-validation --max-retries 3 --delay 2.0

# Full courses generation with all features
python3 generate_courses_from.py --start-from 1 --limit 1000 --save-to-db --ai-validation --max-retries 3 --delay 2.0

# Full course_short generation with all features
python3 generate_course_short_from.py --start-from 1 --limit 1000 --save-to-db --ai-validation --max-retries 3 --delay 2.0
```

### Testing Commands

```bash
# Test single college with all features
python3 generate_overviews_from.py --start-from 1 --limit 1 --save-to-db --ai-validation --max-retries 3

# Dry run to check processing range
python3 generate_overviews_from.py --start-from 100 --limit 10 --dry-run

# Test specific range
python3 generate_overviews_from.py --start-from 1 --end-at 5 --save-to-db --ai-validation
```

### Resuming Processing

```bash
# Resume from where you left off (if processing stopped at college ID 150)
python3 generate_overviews_from.py --start-from 151 --limit 500 --save-to-db --ai-validation --max-retries 3

# Process specific problematic colleges
python3 generate_overviews_from.py --college-ids "45,67,89,123" --save-to-db --ai-validation --max-retries 5
```

## Command Line Options Reference

### Common Options (Available in all enhanced scripts)

- `--start-from <id>`: Start processing from specific college ID
- `--limit <number>`: Limit number of colleges to process
- `--end-at <id>`: End processing at specific college ID
- `--college-ids "1,2,3"`: Process specific college IDs
- `--save-to-db`: Save generated content to database
- `--ai-validation`: Run AI detection validation
- `--max-retries <number>`: Maximum retry attempts for AI scores >90% (default: 3)
- `--delay <seconds>`: Delay between requests in seconds (default: 1.0)
- `--dry-run`: Show what would be processed without actual generation
- `--gptzero-api-key <key>`: Override GPTZero API key
- `--api-key <key>`: Override Google AI API key

### AI Humanization Features

All enhanced scripts include:
- **Automatic retry mechanism**: If AI detection score >90%, automatically retry up to 3 times
- **Humanization tracking**: Track which colleges required humanization retries
- **Statistics reporting**: Detailed stats on retries, success rates, and processing times
- **Score-based persistence**: Only save content if it meets AI detection thresholds

## Script Categories

### Enhanced Scripts (Recommended)

1. `generate_overviews_from.py` - Full college overviews with AI humanization
2. `generate_overview_short_from.py` - Short college summaries with AI humanization
3. `generate_courses_from.py` - Complete course information with AI humanization
4. `generate_course_short_from.py` - Short course summaries with AI humanization

### Legacy Scripts

1. `generate_all_overviews.py` - Basic overview generation (legacy)
2. `main.py` - Single college content generation
3. `batch_process.py` - Multi-college batch processing
4. `run_all_tabs.py` - All content types for single college

### Utility Scripts

1. Environment setup commands
2. Database verification commands
3. Testing and dry-run commands