# Deployment Guide - Railway

## Step-by-Step Deployment Instructions

### Prerequisites
- Railway account (sign up at https://railway.app)
- GitHub account (for code deployment)
- All API keys ready

### Option 1: Deploy via Railway Dashboard (Easiest)

#### Step 1: Create Railway Account
1. Go to https://railway.app
2. Click "Start a New Project"
3. Sign up with GitHub

#### Step 2: Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Connect your GitHub account
4. Create a new repository and push this code:

```bash
cd /home/ubuntu/leasing-intelligence-service
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/leasing-intelligence-service.git
git push -u origin main
```

#### Step 3: Configure Environment Variables
In Railway dashboard, go to Variables tab and add:

```
RENTCAST_API_KEY=f23f2b7122ff4ff58715aa0dbd7540b0
OPENAI_API_KEY=sk-proj-UJsgW1J7ZUrkuZgZ5JHs...
LOVABLE_MARKET_DATA_WEBHOOK=https://qphvrwrmwrfenoeuuuxd.supabase.co/functions/v1/market-data-webhook
LOVABLE_SYNDICATION_WEBHOOK=https://qphvrwrmwrfenoeuuuxd.supabase.co/functions/v1/syndication-results-webhook
LOVABLE_AUTH_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
PORT=8000
```

#### Step 4: Deploy
1. Railway will automatically detect Python and deploy
2. Wait for deployment to complete (2-3 minutes)
3. Click "Generate Domain" to get public URL
4. Copy the URL (e.g., `https://your-service.railway.app`)

#### Step 5: Test Deployment
```bash
curl https://your-service.railway.app/
```

Should return:
```json
{
  "service": "Leasing Intelligence",
  "status": "running",
  "version": "1.0.0"
}
```

### Option 2: Deploy via Railway CLI

#### Step 1: Install Railway CLI
```bash
npm install -g @railway/cli
```

#### Step 2: Login
```bash
railway login
```

#### Step 3: Initialize Project
```bash
cd /home/ubuntu/leasing-intelligence-service
railway init
```

#### Step 4: Set Environment Variables
```bash
railway variables set RENTCAST_API_KEY=f23f2b7122ff4ff58715aa0dbd7540b0
railway variables set OPENAI_API_KEY=sk-proj-UJsgW1J7ZUrkuZgZ5JHs...
railway variables set LOVABLE_MARKET_DATA_WEBHOOK=https://qphvrwrmwrfenoeuuuxd.supabase.co/functions/v1/market-data-webhook
railway variables set LOVABLE_SYNDICATION_WEBHOOK=https://qphvrwrmwrfenoeuuuxd.supabase.co/functions/v1/syndication-results-webhook
railway variables set LOVABLE_AUTH_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### Step 5: Deploy
```bash
railway up
```

#### Step 6: Get Domain
```bash
railway domain
```

### Configure Lovable to Use External Service

Once deployed, you need to tell Lovable to call your external service:

#### Option A: Trigger from Lovable Frontend
Add a button in Lovable that calls your Railway service:

```typescript
// In Lovable React component
const analyzeMarket = async (listingId: string) => {
  const response = await fetch('https://your-service.railway.app/analyze-market', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      listing_id: listingId,
      address: listing.address,
      city: listing.city,
      state: listing.state,
      bedrooms: listing.bedrooms,
      bathrooms: listing.bathrooms,
      square_footage: listing.square_footage,
      current_rent: listing.rent,
      days_on_market: listing.days_on_market,
      property_type: listing.property_type,
      radius: 0.5
    })
  });
  
  return response.json();
};
```

#### Option B: Trigger from Supabase Edge Function
Create a Supabase Edge Function that calls your Railway service:

```typescript
// In Supabase Edge Function
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

serve(async (req) => {
  const { listing_id } = await req.json()
  
  // Fetch listing data from Supabase
  const listing = await supabase
    .from('listings')
    .select('*')
    .eq('id', listing_id)
    .single()
  
  // Call external service
  const response = await fetch('https://your-service.railway.app/analyze-market', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      listing_id: listing.id,
      address: listing.address,
      city: listing.city,
      state: listing.state,
      // ... other fields
    })
  })
  
  return new Response(JSON.stringify({ success: true }), {
    headers: { 'Content-Type': 'application/json' }
  })
})
```

### Set Up Automated Scheduling (Every 7 Days)

#### Option 1: Supabase Cron Job
In Supabase, create a cron job:

```sql
-- Create cron job to analyze all listings weekly
SELECT cron.schedule(
  'analyze-all-listings',
  '0 0 * * 0',  -- Every Sunday at midnight
  $$
  SELECT net.http_post(
    url := 'https://your-service.railway.app/analyze-market',
    headers := '{"Content-Type": "application/json"}'::jsonb,
    body := json_build_object(
      'listing_id', id,
      'address', address,
      'city', city,
      'state', state,
      'bedrooms', bedrooms,
      'bathrooms', bathrooms,
      'square_footage', square_footage,
      'current_rent', rent,
      'days_on_market', days_on_market,
      'property_type', property_type,
      'radius', 0.5
    )::text
  )
  FROM listings
  WHERE status = 'active';
  $$
);
```

#### Option 2: Railway Cron Job
Create a separate Railway service that runs on a schedule:

```python
# cron_job.py
import os
import requests
from supabase import create_client

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Fetch all active listings
listings = supabase.table("listings").select("*").eq("status", "active").execute()

# Analyze each listing
for listing in listings.data:
    requests.post(
        "https://your-service.railway.app/analyze-market",
        json={
            "listing_id": listing["id"],
            "address": listing["address"],
            # ... other fields
        }
    )
```

Deploy this as a separate Railway service with cron schedule.

### Monitoring and Logs

#### View Logs
```bash
railway logs
```

Or in Railway dashboard: Deployments → View Logs

#### Monitor API Usage

**RentCast API:**
- Check usage at https://app.rentcast.io/dashboard
- Free tier: 50 requests/month
- Upgrade if needed: $20/month for 500 requests

**OpenAI API:**
- Check usage at https://platform.openai.com/usage
- Pay-as-you-go pricing
- Expected: ~$1-2/month

**Railway:**
- Check usage at https://railway.app/dashboard
- Free tier: 500 hours/month
- Upgrade if needed: $5/month

### Troubleshooting

#### Service Not Starting
1. Check Railway logs for errors
2. Verify all environment variables are set
3. Check Python version in runtime.txt

#### Webhooks Not Working
1. Verify webhook URLs are correct
2. Check Lovable Supabase logs
3. Test webhooks manually with curl

#### API Errors
1. Verify API keys are valid
2. Check API usage limits
3. Test APIs directly with curl

### Cost Summary

| Service | Free Tier | Paid Tier | Recommended |
|---------|-----------|-----------|-------------|
| Railway | 500 hrs/mo | $5/mo unlimited | Start free |
| RentCast | 50 req/mo | $20/mo (500 req) | Upgrade |
| OpenAI | Pay-as-you-go | ~$1-2/mo | Current |
| **Total** | **~$1-2/mo** | **~$26-27/mo** | **$21-22/mo** |

**Savings vs Lovable AI:** $48-99/month → **$21-22/month** = **$27-77/month saved**

### Next Steps

1. ✅ Deploy to Railway
2. ✅ Test all endpoints
3. ✅ Configure Lovable to call external service
4. ✅ Set up automated scheduling
5. ✅ Monitor API usage
6. ✅ Upgrade RentCast if needed

### Support

If you encounter issues:
1. Check Railway logs
2. Verify environment variables
3. Test locally first
4. Check API documentation
