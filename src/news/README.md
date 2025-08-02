# News Module

This module provides comprehensive financial news fetching and AI-powered analysis capabilities for the WanEye financial dashboard.

## Structure

```
src/news/
├── __init__.py                     # Module exports
├── news_fetcher.py                 # Core news fetching and image processing
└── deepseek_financial_expert.py    # AI-powered financial analysis
```

## Components

### 1. News Fetcher (`news_fetcher.py`)

The main news fetching module that aggregates financial headlines from multiple sources:

- **NewsAPI** - General business news
- **Financial Modeling Prep** - Stock market news
- **Marketaux** - Financial market data
- **GNews** - Global news headlines
- **Yahoo Finance** - Financial RSS feeds
- **Reuters** - Business news RSS
- **Bloomberg** - Market news RSS
- **CNBC** - Business news RSS
- **Financial Times** - FastFT RSS
- **MarketWatch** - Market pulse RSS

#### Key Features:

- **Multi-source aggregation** with randomized weights for balanced coverage
- **Smart image extraction** using browser automation (Playwright) with fallback to traditional scraping
- **AI image generation** for headlines without images using OpenAI DALL-E
- **Dynamic image creation** as ultimate fallback
- **Random headline shuffling** for balanced image processing workload

#### Main Function:

```python
from src.news import fetch_financial_headlines

# Fetch headlines with images and analysis
result = fetch_financial_headlines(test_mode=False)
headlines = result['headlines']  # List of headline dictionaries
analysis = result['analysis']    # AI-generated financial analysis
```

### 2. DeepSeek Financial Expert (`deepseek_financial_expert.py`)

AI-powered financial analysis using the DeepSeek API for comprehensive market insights.

#### Features:

- **Comprehensive Analysis**: Detailed financial analysis with executive summary, market insights, risk assessment, recommendations, and outlook
- **Quick Sentiment Analysis**: Fast sentiment scoring for rapid market pulse checks
- **Professional Formatting**: Markdown-formatted analysis with structured sections
- **Error Handling**: Robust error handling with graceful degradation

#### Usage:

```python
from src.news import create_financial_expert

# Create expert instance
expert = create_financial_expert()

# Check availability
if expert.is_available():
    # Comprehensive analysis
    analysis = expert.analyze_headlines(headlines)
    
    # Quick sentiment check
    sentiment = expert.quick_sentiment_analysis(headlines, max_headlines=10)
    print(f"Sentiment: {sentiment['sentiment']}, Score: {sentiment['score']}/100")
```

#### Class Methods:

- `is_available()` - Check if DeepSeek API is configured
- `analyze_headlines(headlines, max_headlines=20)` - Comprehensive financial analysis
- `quick_sentiment_analysis(headlines, max_headlines=10)` - Fast sentiment scoring

## Configuration

### Required Environment Variables:

```bash
# For DeepSeek Financial Analysis
DEEPSEEK_API_KEY=your_deepseek_api_key

# For AI Image Generation (optional)
OPENAI_API_KEY=your_openai_api_key

# For News Sources (at least one recommended)
NEWSAPI_API_KEY=your_newsapi_key
FMP_API_KEY=your_fmp_key
MARKETAUX_API_KEY=your_marketaux_key
GNEWS_API_KEY=your_gnews_key
```

### Optional Dependencies:

- **Playwright** - For browser automation and enhanced image extraction
- **OpenAI** - For AI-generated images when no web images are found
- **PIL (Pillow)** - For dynamic image generation

## Analysis Output Format

The DeepSeek Financial Expert provides analysis in the following structure:

```markdown
### **Comprehensive Financial Analysis – [Date]**

---

### **1. Executive Summary**
[3-5 key highlights and market sentiment score out of 100]

---

### **2. Key Market Insights**
[Sector/theme breakdown with specific implications]

---

### **3. Risk Assessment**
[Table format with Risk Factor, Impact, Likelihood, and Mitigation columns]

---

### **4. Strategic Recommendations**
[Actionable opportunities and defensive moves with specific tickers]

---

### **5. Market Outlook**
[Short-term and long-term perspectives]
```

## Example Integration

```python
from src.news import fetch_financial_headlines, create_financial_expert

def generate_financial_dashboard():
    # Fetch news with integrated analysis
    news_data = fetch_financial_headlines()
    headlines = news_data['headlines']
    analysis = news_data['analysis']
    
    # Or use expert separately for custom analysis
    expert = create_financial_expert()
    if expert.is_available():
        custom_analysis = expert.analyze_headlines(headlines[:10])
        sentiment = expert.quick_sentiment_analysis(headlines)
    
    return {
        'headlines': headlines,
        'analysis': analysis,
        'sentiment': sentiment
    }
```

## Testing

The module includes test mode for faster CI/CD builds:

```python
# Limit to 1-2 headlines per source for testing
result = fetch_financial_headlines(test_mode=True)
```

## Error Handling

- **Graceful degradation**: If AI analysis fails, the system continues with headline fetching
- **Multiple fallbacks**: Browser automation → Traditional scraping → AI images → Dynamic images
- **Comprehensive logging**: All operations are logged for debugging and monitoring
- **Timeout protection**: All API calls have appropriate timeouts to prevent hanging

## Performance Features

- **Random source weighting**: Distributes load across news sources
- **Headline shuffling**: Balances image processing workload
- **Concurrent processing**: Where possible, operations are parallelized
- **Caching**: Images are cached to avoid re-fetching
- **Test mode**: Reduced load for development and testing
