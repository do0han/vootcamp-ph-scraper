# Vootcamp PH Data Scraper 🇵🇭

A comprehensive data collection bot for Philippines market trends analysis, designed to automatically scrape and aggregate data from multiple online platforms.

## 📋 Overview

This Python-based scraper bot collects real-time trend data from various sources:
- **Google Trends** - Trending searches and related queries
- **Shopee Philippines** - Product trends, flash deals, and sales data  
- **TikTok** - Hashtag trends and viral content analysis

## 🚀 Features

- **Multi-platform scraping** with intelligent bot detection avoidance
- **Supabase integration** for centralized data storage
- **Asynchronous processing** for improved performance
- **Comprehensive error handling** and retry mechanisms
- **Configurable scheduling** for automated data collection
- **Real-time monitoring** and logging

## 📦 Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd vootcamp_ph_scraper
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup environment variables**
```bash
cp env.example .env
# Edit .env with your actual credentials
```

## ⚙️ Configuration

### Required Environment Variables

- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase anon/public key

### Optional Configuration

- `PROXY_HOST`, `PROXY_PORT` - Proxy settings for IP rotation
- `USER_AGENT` - Custom user agent string
- `HEADLESS_MODE` - Run browsers in headless mode (default: true)
- `MAX_RETRIES` - Maximum retry attempts (default: 3)
- `DELAY_BETWEEN_REQUESTS` - Delay between requests in seconds (default: 2)

## 🏃‍♂️ Usage

### Basic Usage
```bash
python main.py
```

### Development Mode
```bash
# Install development dependencies
pip install -r requirements.txt

# Run with debug logging
LOG_LEVEL=DEBUG python main.py
```

### TikTok Scraper Usage Examples

#### Basic TikTok Scraping
```python
import asyncio
from supabase import create_client
from vootcamp_ph_scraper.scrapers.tiktok import TikTokScraper

async def scrape_philippines_trends():
    # Initialize Supabase client
    supabase = create_client(url, key)
    
    # Use TikTok scraper with context manager
    async with TikTokScraper(supabase, headless=True) as scraper:
        # Check ethical compliance
        if not await scraper.check_session_ethics():
            print("Cannot proceed - rate limit reached")
            return
        
        # Scrape Philippines trending content
        videos = await scraper.scrape_hashtag_videos("philippines", limit=20)
        
        # Store data automatically
        success = await scraper.store_data(videos)
        print(f"Collected {len(videos)} videos, stored: {success}")

# Run the scraper
asyncio.run(scrape_philippines_trends())
```

#### Advanced Usage with Monitoring
```python
async def advanced_scraping():
    async with TikTokScraper(database_client) as scraper:
        # Monitor system resources
        resources = await scraper.monitor_system_resources()
        print(f"Memory usage: {resources['memory_usage']:.1f}%")
        
        # Scrape with validation
        videos = await scraper.scrape_hashtag_videos("manila", limit=15)
        
        # Get performance metrics
        metrics = await scraper.get_performance_metrics()
        print(f"Average extraction time: {metrics['average_extraction_time']:.2f}s")
        
        # Check compliance status
        compliance = scraper.get_ethical_compliance_report()
        print(f"Compliance status: {compliance['compliance_status']}")
```

See **[TikTok API Reference](../docs/TIKTOK_API_REFERENCE.md)** for complete method documentation.

## 📁 Project Structure

```
vootcamp_ph_scraper/
├── config/              # Configuration management
│   ├── __init__.py
│   └── settings.py
├── scrapers/            # Data source scrapers
│   ├── __init__.py
│   ├── google_trends.py # ✅ Google Trends scraper
│   ├── shopee.py        # ✅ Shopee scraper
│   └── tiktok.py        # ✅ Advanced TikTok scraper (5,100+ lines)
├── database/            # Database integration
│   ├── __init__.py
│   └── supabase_client.py # (To be implemented)
├── utils/               # Utility functions
│   ├── __init__.py
│   └── helpers.py       # (To be implemented)
├── logs/                # Log files
├── main.py              # Main entry point
├── requirements.txt     # Python dependencies
├── env.example          # Environment variables template
└── README.md            # This file
```

## 🛠️ Development Status

### ✅ Completed
- [x] Project structure setup
- [x] Configuration management
- [x] Environment setup
- [x] Logging system

### ✅ Completed
- [x] **TikTok Scraper** - Advanced hashtag video scraper with comprehensive features
  - Anti-bot detection evasion
  - Data validation and cleaning
  - Performance optimization
  - Ethical scraping compliance
  - Comprehensive error handling
- [x] **Supabase Integration** - Full database connectivity and data storage
- [x] **Google Trends Scraper** - Philippines trending searches and related queries
- [x] **Shopee Scrapers** - Top sales products and flash deals monitoring

### 🚧 In Progress
- [ ] Main orchestration module
- [ ] Additional Shopee categories
- [ ] Advanced analytics dashboard

## 📊 Data Sources

### Google Trends
- Trending searches (24hr Philippines)
- Related queries for target categories
- Regional interest data

### Shopee Philippines  
- Top selling products by keyword
- Flash deal monitoring
- Category trending products
- Price and sales data

### TikTok 🎵
**✅ FULLY IMPLEMENTED** - Advanced TikTok scraper with comprehensive features:
- **Hashtag video collection** with Philippines market targeting
- **Comprehensive data extraction** (videos, metrics, author info, hashtags)
- **Advanced anti-bot countermeasures** with browser fingerprint randomization
- **Infinite scroll handling** with intelligent content discovery
- **Data validation & cleaning** with quality scoring
- **Performance optimization** with batch processing and memory management
- **Ethical scraping compliance** with rate limiting and robots.txt respect
- **Robust error handling** with circuit breaker patterns and recovery strategies

#### 📚 TikTok Scraper Documentation
- **[Main Documentation](../docs/TIKTOK_SCRAPER_DOCUMENTATION.md)** - Complete usage guide and features
- **[API Reference](../docs/TIKTOK_API_REFERENCE.md)** - Detailed method documentation and examples
- **[Troubleshooting & Deployment](../docs/TIKTOK_TROUBLESHOOTING_DEPLOYMENT.md)** - Common issues, solutions, and deployment guides
- **[Ethical Guidelines](../docs/ETHICAL_SCRAPING_GUIDELINES.md)** - Responsible scraping practices

## 🤖 Bot Detection Avoidance

- User agent rotation
- Proxy support
- Request rate limiting
- Browser fingerprint randomization
- Human-like interaction patterns

## 📝 License

This project is for educational and research purposes. Please ensure compliance with each platform's Terms of Service and robots.txt policies.

## 🚀 Deployment

Support for serverless deployment on:
- AWS Lambda
- Google Cloud Functions  
- Vercel Functions

## 📞 Support

For questions or issues, please check the project documentation or create an issue in the repository.

---

**Vootcamp PH** - Empowering Philippines market intelligence through automated data collection. 