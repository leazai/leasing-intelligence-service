# Leasing Intelligence Service

External Python service for real estate leasing intelligence, integrating RentCast API and OpenAI API with a Lovable-built application.

## Overview

This service provides:
- **Market Analysis**: Fetches comparable properties and market statistics using RentCast API
- **Syndication Checking**: Verifies listing presence across 27 major rental sites
- **AI Recommendations**: Generates SEO optimization tips using OpenAI GPT-4

## Architecture

```
Lovable App (React + Supabase)
    ↓ HTTP POST
External Service (FastAPI)
    ↓ API Calls
RentCast API + OpenAI API + Web Scraping
    ↓ Webhook
Lovable Supabase Functions
    ↓ Database
Supabase PostgreSQL
```

## Features

### 1. Market Analysis (`/analyze-market`)
- Fetches rent estimates from RentCast
- Finds comparable properties within configurable radius (0.5-5 miles)
- Calculates market statistics:
  - Average rent
  - Average days on market (DOM)
  - Rent per square foot
  - Active vs rented comparisons
- Sends results to Lovable webhook

### 2. Syndication Check (`/check-syndication`)
- Checks listing presence on 27 rental sites
- Prioritizes top 6 sites: Zillow, Zumper, HotPads, Realtor.com, Redfin, Trulia
- Generates AI-powered SEO recommendations
- Provides site-specific optimization tips
- Sends results to Lovable webhook

## API Endpoints

### Health Check
```bash
GET /
```

### Market Analysis
```bash
POST /analyze-market
Content-Type: application/json

{
  "listing_id": "abc123",
  "address": "123 Main St",
  "city": "Austin",
  "state": "TX",
  "bedrooms": 3,
  "bathrooms": 2.0,
  "square_footage": 1500,
  "current_rent": 2500,
  "days_on_market": 15,
  "property_type": "Single Family",
  "radius": 0.5
}
```

### Syndication Check
```bash
POST /check-syndication
Content-Type: application/json

{
  "listing_id": "abc123",
  "address": "123 Main St",
  "city": "Austin",
  "state": "TX",
  "title": "Beautiful 3BR Home",
  "description": "...",
  "price": 2500,
  "bedrooms": 3,
  "bathrooms": 2.0,
  "square_footage": 1500,
  "amenities": ["Pool", "Garage"],
  "photos_count": 20
}
```

## Environment Variables

Required environment variables (set in Railway):

```bash
# API Keys
RENTCAST_API_KEY=your_rentcast_api_key
OPENAI_API_KEY=your_openai_api_key

# Lovable Webhooks
LOVABLE_MARKET_DATA_WEBHOOK=https://your-supabase-url/functions/v1/market-data-webhook
LOVABLE_SYNDICATION_WEBHOOK=https://your-supabase-url/functions/v1/syndication-results-webhook
LOVABLE_AUTH_TOKEN=your_supabase_anon_key

# Server Config
PORT=8000
```

## Deployment to Railway

### 1. Install Railway CLI
```bash
npm install -g @railway/cli
```

### 2. Login to Railway
```bash
railway login
```

### 3. Initialize Project
```bash
cd leasing-intelligence-service
railway init
```

### 4. Set Environment Variables
```bash
railway variables set RENTCAST_API_KEY=your_key
railway variables set OPENAI_API_KEY=your_key
railway variables set LOVABLE_MARKET_DATA_WEBHOOK=your_webhook
railway variables set LOVABLE_SYNDICATION_WEBHOOK=your_webhook
railway variables set LOVABLE_AUTH_TOKEN=your_token
```

### 5. Deploy
```bash
railway up
```

### 6. Get Service URL
```bash
railway domain
```

## Local Development

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Create .env File
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Run Server
```bash
python main.py
```

Server will start at `http://localhost:8000`

### 4. Test Endpoints
```bash
# Health check
curl http://localhost:8000/

# Test market analysis
python test_market_analysis.py

# Test syndication checker
python test_syndication.py
```

## Project Structure

```
leasing-intelligence-service/
├── main.py                      # FastAPI application
├── rentcast_client.py           # RentCast API client
├── syndication_checker.py       # Syndication checking logic
├── openai_analyzer.py           # OpenAI SEO analyzer
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (local)
├── Procfile                     # Railway start command
├── railway.json                 # Railway configuration
├── runtime.txt                  # Python version
├── test_market_analysis.py      # Test script for market analysis
├── test_syndication.py          # Test script for syndication
└── README.md                    # This file
```

## Cost Savings

This external service saves **$48-99/month** by:
- Using user's OpenAI API (~$1-2/month) instead of Lovable AI ($50-100/month)
- Free Railway hosting (500 hours/month on free tier)
- Free RentCast API (50 requests/month on free tier)

**Total monthly cost: ~$1-2** vs **$50-100** with Lovable AI

## API Usage Limits

### RentCast API (Free Tier)
- 50 requests/month
- For 16 listings checked weekly: 16 × 4 = 64 requests/month
- **Recommendation**: Upgrade to paid tier ($20/month for 500 requests)

### OpenAI API
- Pay-as-you-go pricing
- ~$0.01-0.02 per SEO analysis
- For 16 listings weekly: 16 × 4 × $0.02 = ~$1.28/month

### Railway (Free Tier)
- 500 hours/month (20.8 days)
- $5/month for unlimited hours
- **Recommendation**: Start with free tier, upgrade if needed

## Integration with Lovable

The service sends results to Lovable via webhooks:

1. **Market Data Webhook**: Receives market analysis results
2. **Syndication Webhook**: Receives syndication status and AI recommendations

Lovable stores the data in Supabase and displays it in the UI:
- Listing Performance card: Shows average rent and DOM
- Leasing Signals tab: Shows detailed market analysis
- Syndication Status: Shows which sites have the listing

## Security

- API keys stored as environment variables
- Webhook authentication using Bearer tokens
- CORS enabled for Lovable domain
- HTTPS enforced in production

## Support

For issues or questions:
1. Check Railway logs: `railway logs`
2. Check Lovable Supabase logs
3. Verify environment variables are set correctly
4. Test endpoints locally first

## License

Proprietary - For internal use only
