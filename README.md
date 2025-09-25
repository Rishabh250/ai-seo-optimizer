# Simple AI Content Generator

A clean, minimal implementation for generating college overview and fees content using AI.

## 🎯 Overview

The Simple AI Content Generator is a streamlined tool designed to generate high-quality, SEO-optimized content for educational institutions. It focuses on two core features: overview generation and fees content generation, using Google's Generative AI models.

## ✨ Features

- 🔍 **Overview Generation**: Creates comprehensive college overviews
- 💰 **Fees Content**: Generates detailed fees information  
- 🧹 **Clean Code**: Simplified structure, essential components only
- ⚡ **Simple Usage**: Easy command-line interface
- 🎛️ **Essential Configuration**: Minimal setup required

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- PostgreSQL database with college data
- Google AI API key

### Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set your API key:

```bash
export GOOGLE_API_KEY="your_api_key_here"
```

3. Run the generator:

```bash
# Generate both overview and fees
python main.py --college-id 4

# Generate only overview  
python main.py --college-id 4 --type overview

# Generate only fees
python main.py --college-id 4 --type fees
```

## 📁 Simplified Structure

```
ai-seo-optimizer/
├── main.py                    # Simple main entry point
├── requirements.txt           # Essential dependencies only
├── src/
│   ├── core/
│   │   ├── overview_generator.py  # Overview content generator
│   │   └── fees_generator.py      # Fees content generator
│   ├── services/
│   │   ├── college_service.py     # Database operations
│   │   ├── fees_service.py        # Fees data operations
│   │   └── fees_generator_service.py  # Fees AI generation
│   ├── models/
│   │   ├── generator.py           # Configuration model
│   │   ├── college.py             # College data model
│   │   └── fees.py                # Fees data model
│   ├── database/
│   │   └── manager.py             # Database connection
│   └── utils/
│       ├── prompts.py             # AI prompts
│       ├── fees_prompts.py        # Fees-specific prompts
│       ├── exceptions.py          # Error handling
│       └── logging_config.py      # Simple logging
└── README.md                  # This file
```

## ⚙️ Configuration

### Environment Variables

```bash
# Required
export GOOGLE_API_KEY="your_google_api_key"

# Database (optional, defaults provided)
export DB_HOST="localhost"
export DB_NAME="find_my_college" 
export DB_USER="postgres"
export DB_PASSWORD="your_password"
```

### Command Line Options

```bash
python main.py --help

Options:
  --college-id ID     College ID (required)
  --type TYPE         Content type: overview, fees, both (default: both)
  --api-key KEY       Google API key override
```

## 🔧 What Was Simplified

### Removed Complexity

- ❌ Complex CLI framework
- ❌ Multiple service layers
- ❌ Extensive configuration files
- ❌ Advanced error handling classes
- ❌ Build tools (Makefile, pyproject.toml)
- ❌ Multiple entry points

### Kept Essentials

- ✅ Core AI content generation
- ✅ Database connectivity
- ✅ Basic error handling
- ✅ Simple logging
- ✅ Clean command-line interface

## 📊 Database Requirements

Expected tables:

- `fmc_summary`: College information with `college_id`, `college_name`, `city`, `state`
- `fmc_degree_fees`: Fees data with `college_id`, `degree_name`, `raw_output`

## 🚀 Usage Examples

### Generate Overview Only

```bash
python main.py --college-id 4 --type overview
```

### Generate Fees Only  

```bash
python main.py --college-id 4 --type fees
```

### Generate Both (Default)

```bash
python main.py --college-id 4
```

### With Custom API Key

```bash
python main.py --college-id 4 --api-key "your_key_here"
```

## 🎯 Output

The generator produces clean, SEO-optimized content:

**Overview Content**: Comprehensive institutional information including highlights, rankings, academic programs, facilities, admission process, and student life.

**Fees Content**: Detailed fees information covering all degree programs with tuition structure, payment options, scholarships, facilities, and refund policies.

## 📝 Dependencies

Only essential packages:

- `langchain==0.1.20` - AI framework
- `langchain-google-genai==1.0.10` - Google AI integration  
- `google-generativeai==0.7.2` - Google Generative AI
- `python-dotenv==1.0.0` - Environment variables
- `psycopg2-binary==2.9.9` - PostgreSQL database

Perfect for quick deployment and easy customization!
