# AI SEO Optimizer Scripts Usage Guide

This guide explains how to use the content generation scripts for processing college content across all tabs.

## Available Scripts

### 1. `run_all_tabs.py` - Process Single College
Generates content for all tabs (overview, fees, reviews, courses) for a single college.

#### Usage:
```bash
# Basic usage - process all tabs for a college
python3 run_all_tabs.py --college-id 4141 --api-key YOUR_API_KEY

# Without AI validation (faster)
python3 run_all_tabs.py --college-id 4141 --api-key YOUR_API_KEY --no-ai-validation

# Dry run mode (generate but don't save)
python3 run_all_tabs.py --college-id 4141 --api-key YOUR_API_KEY --dry-run
```

#### Options:
- `--college-id`: Required. The college ID to process
- `--api-key`: Google API key (or set GOOGLE_API_KEY environment variable)
- `--no-ai-validation`: Skip AI validation for faster processing
- `--dry-run`: Generate content but don't save to database

### 2. `batch_process.py` - Process Multiple Colleges
Processes multiple colleges in sequence or parallel.

#### Usage:
```bash
# Process multiple colleges sequentially
python3 batch_process.py --college-ids "4141,4142,4143" --api-key YOUR_API_KEY

# Process colleges in parallel (faster)
python3 batch_process.py --college-ids "4141,4142,4143" --api-key YOUR_API_KEY --parallel

# Limit concurrent processing
python3 batch_process.py --college-ids "4141,4142,4143" --api-key YOUR_API_KEY --parallel --max-concurrent 2

# Without AI validation
python3 batch_process.py --college-ids "4141,4142,4143" --api-key YOUR_API_KEY --no-ai-validation
```

#### Options:
- `--college-ids`: Required. Comma-separated list of college IDs
- `--api-key`: Google API key (or set GOOGLE_API_KEY environment variable)
- `--parallel`: Process colleges in parallel
- `--max-concurrent`: Maximum concurrent colleges (default: 3)
- `--no-ai-validation`: Skip AI validation for faster processing

## Content Generation Process

Each script processes the following content types in order:

1. **Overview** (`overview` tab)
   - Generates comprehensive college overview content
   - Includes location, facilities, programs, etc.

2. **Fees** (`fees` tab)
   - Generates detailed fees breakdown
   - Covers all degree programs and fee structures

3. **Reviews** (`reviews` tab)
   - Generates content based on college reviews
   - Highlights strengths and student experiences

4. **Courses** (`all_courses` tab)
   - Generates detailed course information
   - Covers all available programs and degrees

5. **Campus** (`campus` tab)
   - Generates campus infrastructure content
   - Covers facilities, laboratories, amenities, etc.

## Database Integration

The scripts automatically:

1. **Save to `content_analysis` table**: All generated content with metadata
2. **AI Validation**: Optional GPTZero integration for AI detection
3. **Smart Persistence**: Only saves content with better AI scores than previous versions
4. **Tab Content**: Saves to `fmc_content_tabs` table for frontend display

## AI Validation Features

When AI validation is enabled:
- Content is analyzed using GPTZero API
- AI probability scores are calculated
- Only content with lower AI scores than previous versions is saved to tabs
- All content is saved to `content_analysis` for tracking

## Output Format

### Single College Processing:
```
INFO:🏫 Processing college ID: 4141
INFO:🤖 AI Validation: Enabled
INFO:📊 Processing 5 content types with AI validation: True

INFO:📄 [1/5] Generating overview content...
INFO:✅ [1/5] Overview content completed successfully

INFO:💰 [2/5] Generating fees content...  
INFO:✅ [2/5] Fees content completed successfully

INFO:⭐ [3/5] Generating reviews content...
INFO:✅ [3/5] Reviews content completed successfully

INFO:📚 [4/5] Generating courses content...
INFO:✅ [4/5] Courses content completed successfully

INFO:🏫 [5/5] Generating campus content...
INFO:✅ [5/5] Campus content completed successfully

INFO:🎯 Content generation summary for college 4141:
INFO:   📊 Completed: 5/5 tabs
INFO:   📄 Overview: ✅
INFO:   💰 Fees: ✅  
INFO:   ⭐ Reviews: ✅
INFO:   📚 Courses: ✅
INFO:   🏫 Campus: ✅
```

### Batch Processing Summary:
```
INFO:📊 BATCH PROCESSING SUMMARY
INFO:✅ College 4141: SUCCESS (5/5 tabs)
INFO:⚠️ College 4142: PARTIAL (4/5 tabs)
INFO:❌ College 4143: FAILED - API key not valid

INFO:📈 FINAL STATISTICS:
INFO:   🎯 Total Colleges: 3
INFO:   ✅ Successful: 1
INFO:   ⚠️ Partial: 1
INFO:   ❌ Failed: 1
INFO:   📊 Success Rate: 33.3%
```

## Environment Setup

### Set API Key:
```bash
export GOOGLE_API_KEY="your_api_key_here"
```

### Make Scripts Executable:
```bash
chmod +x run_all_tabs.py batch_process.py
```

## Examples

### Process Single College with Full Features:
```bash
python3 run_all_tabs.py --college-id 4141 --api-key $GOOGLE_API_KEY
```

### Batch Process Without AI Validation:
```bash
python3 batch_process.py --college-ids "4141,4142,4143,4144,4145" --no-ai-validation
```

### Parallel Processing with Rate Limiting:
```bash
python3 batch_process.py --college-ids "4141,4142,4143,4144,4145" --parallel --max-concurrent 2
```

## Error Handling

The scripts handle:
- Invalid API keys
- Network timeouts
- Database connection issues
- Content generation failures
- AI validation service errors

Failed operations are logged and processing continues for remaining items.

## Performance Recommendations

1. **Use `--no-ai-validation`** for faster processing
2. **Use `--parallel`** for batch processing
3. **Limit `--max-concurrent`** to avoid API rate limits
4. **Monitor logs** for detailed progress information

## Exit Codes

- `0`: Success - all content generated successfully
- `1`: Failure - critical error or no content generated
- `2`: Partial success - some content generated, some failed
