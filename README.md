# Structured Extraction API

A modular FastAPI system for extracting structured data from text content and URLs using OpenAI's structured outputs capability with auto-discovery schema registration.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-orange.svg)](https://openai.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🚀 Features

- **🔄 Auto-Discovery**: Automatically discovers and registers new extraction schemas without code changes
- **📝 Multiple Input Types**: Process raw text or scrape content from URLs using Playwright
- **🎯 Predefined Schemas**: Ready-to-use extraction schemas for notes, bookmarks, books, job postings
- **⚡ Zero Configuration**: Just add a new schema file and it's automatically available via API
- **📁 Smart File Management**: Configurable saving of markdown content and JSON results with deduplication
- **🐳 Docker Ready**: Full containerization with Docker and docker-compose
- **🔧 Modern Stack**: FastAPI, Pydantic, OpenAI structured outputs, uv for dependency management
- **📊 Advanced Logging**: Loguru-based structured logging with metrics and file rotation
- **🎨 Clean Architecture**: SOLID principles with clear separation of concerns

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Usage](#api-usage)
- [Available Schemas](#available-schemas)
- [Adding New Schemas](#adding-new-schemas)
- [Project Structure](#project-structure)
- [Logging](#logging)
- [Development](#development)
- [Docker Setup](#docker-setup)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key
- uv (recommended) or pip

### 1-Minute Setup

```bash
# Clone and setup
git clone <repository-url>
cd structured-extraction-api

# Install with setup script
chmod +x setup.sh
./setup.sh

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Start the server
uv run uvicorn app.main:app --reload
```

🎉 **That's it!** API is now running at `http://localhost:8000`

📖 **Documentation**: `http://localhost:8000/docs`

## 📦 Installation

### Option 1: Manual Installation

```bash
# Clone repository
git clone <repository-url>
cd structured-extraction-api

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Install Playwright browsers
uv run playwright install chromium

# Setup environment
cp .env.example .env
# Edit .env with your configuration
```

### Option 2: Docker Installation

```bash
# Clone repository
git clone <repository-url>
cd structured-extraction-api

# Setup environment
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

# Run with Docker
docker-compose up --build
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file from `.env.example`:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional - API Configuration
OPENAI_MODEL=gpt-4o-2024-08-06
DEBUG=true

# Optional - Logging
LOG_LEVEL=INFO
LOG_TO_FILE=true
LOG_FILE_PATH=logs/app.log
LOG_ROTATION=10 MB
LOG_RETENTION=1 month

# Optional - Storage
DATA_DIR=data
MARKDOWN_OUTPUT_DIR=data/markdown
JSON_OUTPUT_DIR=data/json

# Optional - Scraper
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_TIMEOUT=60000
```

### Configuration Details

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | - | ✅ |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4o-2024-08-06` | ❌ |
| `DEBUG` | Enable debug mode | `false` | ❌ |
| `LOG_LEVEL` | Logging level | `INFO` | ❌ |
| `LOG_TO_FILE` | Enable file logging | `true` | ❌ |
| `DATA_DIR` | Base data directory | `data` | ❌ |
| `PLAYWRIGHT_HEADLESS` | Run browser headless | `true` | ❌ |

## 🌐 API Usage

### Base URL
- **Local**: `http://localhost:8000`
- **Docker**: `http://localhost:8000`

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/extraction/extract` | Extract structured data |
| `GET` | `/api/v1/extraction/schemas` | List available schemas |
| `GET` | `/api/v1/extraction/schemas/{type}` | Get schema details |
| `GET` | `/api/v1/extraction/health` | Health check |

### Extract from Text

```bash
curl -X POST "http://localhost:8000/api/v1/extraction/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "text",
    "content": "Meeting notes: Discussed Q4 budget planning. Action items: 1) Review expenses 2) Prepare presentation",
    "extraction_type": "notes",
    "save_json": true
  }'
```

### Extract from URL

```bash
curl -X POST "http://localhost:8000/api/v1/extraction/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "url",
    "content": "https://example.com/job-posting",
    "extraction_type": "job_postings",
    "save_markdown": true,
    "save_json": true
  }'
```

### Response Format

```json
{
  "success": true,
  "extraction_type": "notes",
  "extracted_data": {
    "notes": [
      {
        "title": "Q4 Budget Planning",
        "content": "Discussed Q4 budget planning meeting",
        "summary": "Team meeting about budget review"
      }
    ],
    "main_topics": ["budget", "planning", "Q4"],
    "tags": [{"name": "meeting", "category": "business"}],
    "priority": "medium",
    "category": "business"
  },
  "json_path": "data/json/notes_a1b2c3d4_20240115_143022.json",
  "processing_time": 2.34,
  "timestamp": "2024-01-15T14:30:22.123456",
  "token_usage": {
    "prompt_tokens": 150,
    "completion_tokens": 200,
    "total_tokens": 350
  }
}
```

### Request Parameters

#### Required
- `input_type`: `"text"` or `"url"`
- `content`: Text content or URL to process
- `extraction_type`: Schema type (see [Available Schemas](#available-schemas))

#### Optional
- `save_markdown`: Save scraped content as markdown (default: `false`)
- `save_json`: Save extracted data as JSON (default: `true`)
- `output_directory`: Custom output directory
- `filename_prefix`: Custom filename prefix
- `custom_instructions`: Additional extraction instructions

## 📚 Available Schemas

### 📝 Notes (`notes`)
Extract and organize text into structured notes with topics, tags, and priorities.

**Use cases**: Meeting notes, research notes, personal notes
**Output**: Notes with titles, summaries, topics, tags, priority levels

### 🔖 Bookmarks (`bookmarks`)
Organize content into categorized bookmarks with metadata.

**Use cases**: Article bookmarking, resource organization, reading lists
**Output**: Title, description, category, tags, importance score, reading time

### 📚 Books (`books`)
Extract comprehensive book information and metadata.

**Use cases**: Book cataloging, library management, reading tracking
**Output**: Title, authors, ISBN, publication info, genres, reviews

### 💼 Job Postings (`job_postings`)
Parse job postings with requirements, responsibilities, and compensation.

**Use cases**: Job analysis, recruitment tracking, market research
**Output**: Job details, requirements, salary, benefits, application info

### List All Available Schemas

```bash
curl "http://localhost:8000/api/v1/extraction/schemas"
```

### Get Schema Details

```bash
curl "http://localhost:8000/api/v1/extraction/schemas/notes"
```

## ➕ Adding New Schemas

The system uses **auto-discovery** - just create a new schema file and it's automatically available!

### 1. Create Schema File

Create `app/models/schemas/invoices.py`:

```python
from typing import List, Optional
from pydantic import BaseModel, Field
from ..base import BaseExtractionSchema

class InvoiceItem(BaseModel):
    description: str = Field(..., description="Item description")
    quantity: int = Field(..., description="Quantity")
    unit_price: float = Field(..., description="Unit price")
    total: float = Field(..., description="Line total")

class InvoiceExtraction(BaseExtractionSchema):
    # Schema definition
    invoice_number: str = Field(..., description="Invoice number")
    date: str = Field(..., description="Invoice date")
    vendor: str = Field(..., description="Vendor name")
    items: List[InvoiceItem] = Field(..., description="Invoice items")
    subtotal: float = Field(..., description="Subtotal")
    tax: float = Field(..., description="Tax amount")
    total: float = Field(..., description="Total amount")
    
    # Auto-discovery configuration
    extraction_type = "invoices"
    description = "Extracts invoice data with line items and totals"
    prompt = """You are an invoice processing expert. Extract comprehensive invoice information.
    
    Focus on:
    - Identifying invoice numbers and dates
    - Extracting vendor information
    - Itemizing all line items with quantities and prices
    - Calculating subtotals, taxes, and totals
    - Ensuring numerical accuracy
    
    Be precise with all financial data."""
```

### 2. Test Your Schema

```bash
# Restart the server (if running)
# The schema is automatically discovered!

curl -X POST "http://localhost:8000/api/v1/extraction/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "input_type": "text",
    "content": "Invoice #12345 from ABC Corp. Items: 2x Widget ($10 each), 1x Gadget ($25). Subtotal: $45, Tax: $4.50, Total: $49.50",
    "extraction_type": "invoices",
    "save_json": true
  }'
```

### Schema Requirements

Your schema must:
1. Inherit from `BaseExtractionSchema`
2. Define these class attributes:
   - `extraction_type`: Unique identifier
   - `description`: Human-readable description
   - `prompt`: System prompt for OpenAI
3. Use Pydantic Field descriptions for all fields

## 🏗️ Project Structure

```
structured-extraction-api/
├── app/
│   ├── api/v1/                    # API routes
│   │   ├── endpoints/
│   │   │   └── extraction.py      # Extraction endpoints
│   │   └── router.py              # Route aggregation
│   ├── core/                      # Core business logic
│   │   ├── content_scraper.py     # URL content scraping
│   │   ├── extraction_engine.py   # OpenAI integration
│   │   └── file_manager.py        # File operations
│   ├── models/                    # Data models
│   │   ├── base.py                # Base classes
│   │   ├── requests.py            # Request models
│   │   ├── responses.py           # Response models
│   │   └── schemas/               # Extraction schemas
│   │       ├── notes.py           # Notes extraction
│   │       ├── bookmarks.py       # Bookmarks extraction
│   │       ├── books.py           # Books extraction
│   │       └── job_postings.py    # Job postings extraction
│   ├── services/                  # Service layer
│   │   ├── extraction_service.py  # Main extraction orchestrator
│   │   └── schema_registry.py     # Auto-discovery registry
│   └── utils/                     # Utilities
│       ├── exceptions.py          # Custom exceptions
│       └── logging_manager.py     # Loguru configuration
├── data/                          # Output files
│   ├── json/                      # Extracted JSON data
│   └── markdown/                  # Scraped markdown content
├── logs/                          # Log files
├── Dockerfile                     # Docker configuration
├── docker-compose.yml             # Docker Compose setup
├── pyproject.toml                 # Python dependencies
└── README.md                      # This file
```

## 📊 Logging

### Features
- **Structured Logging**: Key-value pairs with context
- **File Rotation**: Automatic log rotation (10MB default)
- **Colored Console**: Beautiful development output
- **Metrics Tracking**: Automatic performance metrics
- **Multiple Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL

### Configuration

```bash
# Environment variables
LOG_LEVEL=INFO           # Set logging level
LOG_TO_FILE=true         # Enable file logging
LOG_FILE_PATH=logs/app.log
LOG_ROTATION=10 MB       # Rotate at 10MB
LOG_RETENTION=1 month    # Keep for 1 month
```

### Example Logs

```
2024-01-15 10:30:45 | INFO     | app.services.extraction_service:process_extraction:45 | Processing extraction request | extraction_type=notes input_type=text
2024-01-15 10:30:47 | SUCCESS  | app.core.extraction_engine:extract_structured_data:78 | Successfully extracted data for notes | processing_time=1.23 tokens_used=450
2024-01-15 10:30:47 | INFO     | app.core.file_manager:save_json:67 | Saved JSON file: notes_a1b2c3d4_20240115_143022.json | filepath=data/json/notes_a1b2c3d4_20240115_143022.json
```

### Development Logging

```python
from app.utils.logging_manager import LoggingManager

# Change log level dynamically
LoggingManager.set_level("DEBUG")

# Add custom log file
LoggingManager.add_file_handler("logs/debug.log", "DEBUG")
```

## 🔧 Development

### Setup Development Environment

```bash
# Clone repository
git clone <repository-url>
cd structured-extraction-api

# Install with dev dependencies
uv sync --dev

# Install pre-commit hooks (optional)
pre-commit install

# Run in development mode
uv run uvicorn app.main:app --reload --log-level debug
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app

# Run specific test file
uv run pytest tests/test_extraction.py

# Run with verbose output
uv run pytest -v
```

### Code Quality

```bash
# Format code
uv run black app/

# Lint code
uv run ruff check app/

# Type checking
uv run mypy app/
```

### Development Commands

```bash
# Add new dependency
uv add package-name

# Add development dependency
uv add --dev package-name

# Update dependencies
uv sync --upgrade

# Run specific script
uv run python -m app.scripts.my_script
```

## 🐳 Docker Setup

### Quick Start with Docker

```bash
# Clone repository
git clone <repository-url>
cd structured-extraction-api

# Setup environment
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Docker Configuration

The Docker setup includes:
- **Multi-stage build** for optimized image size
- **Health checks** for service monitoring
- **Volume mounts** for persistent data and logs
- **Environment configuration** via .env file
- **Automatic dependency installation** with uv

### Production Deployment

```bash
# Build production image
docker build -t structured-extraction-api:latest .

# Run production container
docker run -d \
  --name extraction-api \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_key_here \
  -e DEBUG=false \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  structured-extraction-api:latest
```

## 📖 Examples

### JavaScript/TypeScript Client

```javascript
class ExtractionClient {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async extract(request) {
    const response = await fetch(`${this.baseUrl}/api/v1/extraction/extract`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  }

  async getSchemas() {
    const response = await fetch(`${this.baseUrl}/api/v1/extraction/schemas`);
    return await response.json();
  }
}

// Usage
const client = new ExtractionClient();

const result = await client.extract({
  input_type: 'text',
  content: 'Your content here...',
  extraction_type: 'notes',
  save_json: true
});

console.log('Extracted data:', result.extracted_data);
```

### Python Client

```python
import requests
from typing import Dict, Any

class ExtractionClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def extract(self, request: Dict[str, Any]) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/api/v1/extraction/extract",
            json=request
        )
        response.raise_for_status()
        return response.json()

    def get_schemas(self) -> Dict[str, Any]:
        response = requests.get(f"{self.base_url}/api/v1/extraction/schemas")
        response.raise_for_status()
        return response.json()

# Usage
client = ExtractionClient()

result = client.extract({
    "input_type": "text",
    "content": "Your content here...",
    "extraction_type": "notes",
    "save_json": True
})

print("Extracted data:", result["extracted_data"])
```

### Batch Processing Script

```bash
#!/bin/bash
# process_urls.sh - Process multiple URLs

urls=(
  "https://example.com/article1"
  "https://example.com/article2"
  "https://example.com/article3"
)

for url in "${urls[@]}"; do
  echo "Processing: $url"
  
  curl -X POST "http://localhost:8000/api/v1/extraction/extract" \
    -H "Content-Type: application/json" \
    -d "{
      \"input_type\": \"url\",
      \"content\": \"$url\",
      \"extraction_type\": \"bookmarks\",
      \"save_json\": true,
      \"save_markdown\": true
    }" \
    --silent | jq '.success'
  
  echo "Completed: $url"
  sleep 1  # Rate limiting
done

echo "Batch processing completed!"
```

## 🔍 Troubleshooting

### Common Issues

#### OpenAI API Key Issues
```bash
# Error: OpenAI API key is required
# Solution: Check your .env file
cat .env | grep OPENAI_API_KEY
```

#### Playwright Browser Issues
```bash
# Error: Browser not found
# Solution: Install browsers
uv run playwright install chromium
```

#### Permission Issues
```bash
# Error: Permission denied for data directory
# Solution: Fix permissions
chmod 755 data/
chmod 755 logs/
```

#### Port Already in Use
```bash
# Error: Port 8000 already in use
# Solution: Use different port
uv run uvicorn app.main:app --port 8001
```

### Debug Mode

Enable debug mode for detailed logging:

```bash
# Set environment variable
export DEBUG=true
export LOG_LEVEL=DEBUG

# Or in .env file
DEBUG=true
LOG_LEVEL=DEBUG
```

### Health Check

```bash
# Check if API is running
curl http://localhost:8000/api/v1/extraction/health

# Expected response
{"status": "healthy", "service": "structured-extraction-api"}
```

### Log Analysis

```bash
# View recent logs
tail -f logs/app.log

# Search for errors
grep "ERROR" logs/app.log

# Filter by extraction type
grep "extraction_type=notes" logs/app.log
```

### Performance Issues

```bash
# Check processing times in logs
grep "processing_time" logs/app.log | tail -10

# Monitor token usage
grep "tokens_used" logs/app.log | tail -10

# Check file sizes
du -sh data/json/
du -sh data/markdown/
```

## 🤝 Contributing

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/new-schema
   ```
3. **Make your changes**
4. **Add tests**
   ```bash
   uv run pytest tests/test_new_schema.py
   ```
5. **Run quality checks**
   ```bash
   uv run black app/
   uv run ruff check app/
   ```
6. **Commit your changes**
   ```bash
   git commit -m "Add new schema for invoices"
   ```
7. **Push and create PR**

### Adding New Features

#### New Extraction Schema
1. Create schema file in `app/models/schemas/`
2. Follow existing patterns
3. Add tests in `tests/schemas/`
4. Update documentation

#### New API Endpoint
1. Add endpoint in `app/api/v1/endpoints/`
2. Update router in `app/api/v1/router.py`
3. Add tests in `tests/api/`
4. Update OpenAPI documentation

### Code Standards

- **Python Style**: Black formatter, Ruff linter
- **Type Hints**: All functions should have type hints
- **Docstrings**: All public methods need docstrings
- **Tests**: New features require tests
- **Logging**: Use structured logging with LoggingManager

### Issue Templates

When reporting issues, please include:
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Relevant log excerpts

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for structured outputs API
- **FastAPI** for the excellent web framework
- **Playwright** for robust web scraping
- **Loguru** for beautiful logging
- **Pydantic** for data validation

## 🔗 Links

- **Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **OpenAI API**: [https://platform.openai.com/docs](https://platform.openai.com/docs)
- **FastAPI Docs**: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
- **Playwright Docs**: [https://playwright.dev/python/](https://playwright.dev/python/)

---

**Made with ❤️ for structured data extraction**