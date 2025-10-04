# Waneye Financial Overview

[![Unit Tests](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/test.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/test.yml)
[![Code Quality](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/quality.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/quality.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

This project fetches financial headlines from multiple sources, generates a modern HTML dashboard (index.html) with cards for each headline (including images), and displays additional financial data like central bank rates, economic indicators, and forex information.

## Features

- 🏦 **Financial News Aggregation** - Collects headlines from multiple sources
- 🎨 **Template-Based HTML Generation** - Uses Jinja2 templates for clean, maintainable code
- 🖼️ **Dynamic Image Generation** - AI-generated images for headlines without pictures
- 📱 **Responsive Design** - Modern, mobile-friendly interface
- ⚡ **Performance Optimized** - Image lazy loading and resource optimization
- 🧪 **Comprehensive Testing** - Full unit test coverage with pytest

## How to Use
1. Ensure you have Python 3.8+ installed.
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Set required API keys as environment variables:
   ```sh
   export OPENAI_API_KEY=your_api_key_here  # Required for AI image generation
   export NEWSAPI_API_KEY=your_api_key_here  # Optional for additional news sources
   export FMP_API_KEY=your_api_key_here      # Optional for additional news sources
   export MARKETAUX_API_KEY=your_api_key_here  # Optional for additional news sources
   export GNEWS_API_KEY=your_api_key_here    # Optional for additional news sources
   ```
4. Run the site generator:
   ```sh
   python generate_site.py
   ```
5. Open `index.html` in your browser to view the dashboard.

## Testing

This project includes comprehensive unit tests to ensure reliability and maintainability.

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run specific test file
python -m pytest tests/test_template_generation.py

# Run with coverage
python -m pytest --cov=src tests/
```

### Test Coverage

- **Template Generation**: Tests for Jinja2-based HTML generation
- **Image Processing**: Tests for dynamic and AI-generated images
- **Data Processing**: Tests for news, economic data, and forex handling
- **Error Handling**: Tests for graceful error handling and logging

### Continuous Integration

All pull requests automatically run:
- Unit tests across Python 3.9-3.13
- Code quality checks (formatting, linting, security)
- Build validation tests

See [TEST_SUITE.md](TEST_SUITE.md) for detailed testing documentation.

## Project Files
- `generate_site.py`: Main script to fetch data and generate the dashboard.
- `src/news.py`: Logic for fetching headlines, images, and generating AI images when needed.
- `src/htmlgen.py`: HTML generation for the dashboard with responsive design.
- `src/central_banks.py`: Fetches central bank data.
- `src/economic_data.py`: Fetches economic indicators.
- `src/forex_data.py`: Fetches forex exchange rates.
- `static/`: Contains CSS, JS, and images used in the dashboard.
- `.github/copilot-instructions.md`: Copilot custom instructions.

## Notes
- OpenAI API key is required for generating images for headlines when no image can be fetched.
- Without an OpenAI API key, the system will fall back to using colorful default images.
- At least one news API key is recommended for fetching headlines, but the system will attempt to fetch from available free sources if no API keys are provided.
- The dashboard is generated statically and can be hosted on any web server.
- The script is designed for educational and demonstration purposes.
