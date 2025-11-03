# ============================================================================
# FILE: main.py
# VERSION: 2.0 - WITH EMOJI DEBUG LOGGING
# LAST UPDATED: 2025-11-03
# ============================================================================
# START OF FILE - DO NOT DELETE THIS LINE
# ============================================================================

"""
Leasing Intelligence Service
FastAPI web service for market analysis and syndication checking
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
import requests
import httpx
import json

from rentcast_client import RentCastClient
from syndication_checker import SyndicationChecker
from openai_analyzer import OpenAIAnalyzer
from showmojo_client import ShowMojoClient

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Leasing Intelligence Service",
    description="Market analysis and syndication checking for rental listings",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
rentcast_client = RentCastClient(api_key=os.getenv("RENTCAST_API_KEY"))
syndication_checker = SyndicationChecker()
openai_analyzer = OpenAIAnalyzer(api_key=os.getenv("OPENAI_API_KEY"))
showmojo_client = ShowMojoClient(
    email=os.getenv("SHOWMOJO_EMAIL"),
    password=os.getenv("SHOWMOJO_PASSWORD")
)

# Lovable webhook URLs
LOVABLE_MARKET_WEBHOOK = os.getenv("LOVABLE_MARKET_DATA_WEBHOOK")
LOVABLE_SYNDICATION_WEBHOOK = os.getenv("LOVABLE_SYNDICATION_WEBHOOK")
LOVABLE_SHOWINGS_WEBHOOK = os.getenv("LOVABLE_SHOWINGS_WEBHOOK", LOVABLE_MARKET_WEBHOOK)  # Fallback to market webhook
LOVABLE_AUTH_TOKEN = os.getenv("LOVABLE_AUTH_TOKEN")


# Request models
class MarketAnalysisRequest(BaseModel):
    listing_id: str
    address: str
    city: str
    state: str
    bedrooms: int
    bathrooms: float
    square_footage: int
    current_rent: int
    days_on_market: int
    property_type: str = "Single Family"
    radius: float = 0.5


class SyndicationCheckRequest(BaseModel):
    listing_id: str
    address: str
    city: str
    state: str
    title: str
    description: str
    price: int
    bedrooms: int
    bathrooms: float
    square_footage: int
    amenities: List[str]
    photos_count: int


class ShowingsRequest(BaseModel):
    days_back: int = 30
    property_id: Optional[str] = None


# Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Leasing Intelligence",
        "status": "running",
        "version": "1.0.0"
    }


@app.post("/analyze-market")
async def analyze_market(request: MarketAnalysisRequest, background_tasks: BackgroundTasks):
    """
    Analyze market data for a listing using RentCast API
    Sends results to Lovable webhook
    """
    try:
        # Start analysis in background
        background_tasks.add_task(
            _process_market_analysis,
            request
        )
        
        return {
            "status": "processing",
            "message": "Market analysis started",
            "listing_id": request.listing_id
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/check-syndication")
async def check_syndication(request: SyndicationCheckRequest, background_tasks: BackgroundTasks):
    """
    Check syndication status and generate SEO recommendations
    Sends results to Lovable webhook
    """
    try:
        # Start check in background
        background_tasks.add_task(
            _process_syndication_check,
            request
        )
        
        return {
            "status": "processing",
            "message": "Syndication check started",
            "listing_id": request.listing_id
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sync-showings")
async def sync_showings(request: ShowingsRequest, background_tasks: BackgroundTasks):
    """
    Sync showing data from ShowMojo
    Fetches showing data and sends to Lovable webhook
    """
    try:
        # Start sync in background
        background_tasks.add_task(
            _process_showings_sync,
            request
        )
        
        return {
            "status": "processing",
            "message": "Showing data sync started",
            "days_back": request.days_back
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Background tasks
async def _process_market_analysis(request: MarketAnalysisRequest):
    """Process market analysis and send to Lovable"""
    try:
        print(f"Starting market analysis for {request.address}...")
        
        # Get market data from RentCast
        market_data = rentcast_client.get_market_data(
            address=f"{request.address}, {request.city}, {request.state}",
            bedrooms=request.bedrooms,
            bathrooms=request.bathrooms,
            square_footage=request.square_footage,
            property_type=request.property_type,
            radius=request.radius
        )
        
        if not market_data.get("success"):
            print(f"Market analysis failed: {market_data.get('error')}")
            return
        
        # Prepare data for Lovable
        market_stats = market_data.get("market_stats", {})
        comparables = market_data.get("comparables", [])
        
        # Calculate listing vs market
        listing_rent_per_sqft = round(request.current_rent / request.square_footage, 2) if request.square_footage > 0 else 0
        market_avg_rent = market_stats.get("market_avg_rent", 0)
        rent_vs_market_pct = round(((request.current_rent - market_avg_rent) / market_avg_rent * 100), 2) if market_avg_rent > 0 else 0
        
        market_avg_dom = market_stats.get("market_avg_dom", 0)
        dom_vs_market_pct = round(((request.days_on_market - market_avg_dom) / market_avg_dom * 100), 2) if market_avg_dom > 0 else 0
        
        # Build payload for Lovable
        payload = {
            "listing_id": request.listing_id,
            "radius": request.radius,
            **market_stats,
            "listing_rent_per_sqft": listing_rent_per_sqft,
            "rent_vs_market_pct": rent_vs_market_pct,
            "dom_vs_market_pct": dom_vs_market_pct,
            "comparables": [
                {
                    "comp_address": c.get("address", ""),
                    "comp_rent": c.get("price", 0),
                    "comp_rent_per_sqft": round(c.get("price", 0) / c.get("squareFootage", 1), 2) if c.get("squareFootage") else 0,
                    "comp_bedrooms": c.get("bedrooms", 0),
                    "comp_bathrooms": c.get("bathrooms", 0),
                    "comp_square_footage": c.get("squareFootage", 0),
                    "comp_days_on_market": c.get("daysOnMarket", 0),
                    "comp_status": c.get("status", "Unknown"),
                    "distance": c.get("distance", 0)
                }
                for c in comparables[:50]  # Limit to 50 comps
            ]
        }
        
        # Send to Lovable webhook
        async with httpx.AsyncClient() as client:
            response = await client.post(
                LOVABLE_MARKET_WEBHOOK,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {LOVABLE_AUTH_TOKEN}"
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                print(f"Market data sent to Lovable successfully for {request.listing_id}")
            else:
                print(f"Failed to send to Lovable: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"Error in market analysis: {e}")


async def _process_syndication_check(request: SyndicationCheckRequest):
    """Process syndication check and send to Lovable"""
    try:
        print(f"Starting syndication check for {request.address}...")
        
        # Check syndication sites
        syndication_results = syndication_checker.check_all_sites(
            address=request.address,
            city=request.city,
            state=request.state
        )
        
        print(f"Syndication check complete: {syndication_results['total_sites_found']}/27 sites found")
        
        # Get market data for AI context (optional, use cached if available)
        market_data = rentcast_client.get_market_data(
            address=f"{request.address}, {request.city}, {request.state}",
            bedrooms=request.bedrooms,
            bathrooms=request.bathrooms,
            square_footage=request.square_footage,
            radius=0.5
        )
        
        # Generate AI recommendations
        print("Generating AI SEO recommendations...")
        ai_analysis = openai_analyzer.analyze_listing_seo(
            address=request.address,
            title=request.title,
            description=request.description,
            price=request.price,
            bedrooms=request.bedrooms,
            bathrooms=request.bathrooms,
            square_footage=request.square_footage,
            amenities=request.amenities,
            photos_count=request.photos_count,
            syndication_results=syndication_results,
            market_data=market_data
        )
        
        print(f"AI analysis complete: SEO score {ai_analysis.get('overall_seo_score', 0)}/100")
        
        # Build payload for Lovable
        payload = {
            "listing_id": request.listing_id,
            **syndication_results,
            "overall_seo_score": ai_analysis.get("overall_seo_score", 50),
            "site_scores": ai_analysis.get("site_scores", {}),
            "ai_recommendations": {
                "quick_wins": ai_analysis.get("quick_wins", []),
                "high_priority_actions": ai_analysis.get("high_priority_actions", []),
                "site_specific_tips": ai_analysis.get("site_specific_tips", {})
            }
        }
        
        # Send to Lovable webhook
        async with httpx.AsyncClient() as client:
            response = await client.post(
                LOVABLE_SYNDICATION_WEBHOOK,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {LOVABLE_AUTH_TOKEN}"
                },
                timeout=60.0
            )
            
            if response.status_code == 200:
                print(f"Syndication results sent to Lovable successfully for {request.listing_id}")
            else:
                print(f"Failed to send to Lovable: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"Error in syndication check: {e}")


async def _process_showings_sync(request: ShowingsRequest):
    """Process ShowMojo showing data sync and send to Lovable"""
    try:
        print(f"🔄 Starting ShowMojo sync for last {request.days_back} days...")
        
        # Fetch showing data from ShowMojo
        showings_data = showmojo_client.get_showings(
            days_back=request.days_back,
            property_id=request.property_id
        )
        
        if not showings_data.get("success"):
            print(f"❌ ShowMojo sync failed: {showings_data.get('error')}")
            return
        
        showings = showings_data.get("showings", [])
        print(f"✅ Retrieved {len(showings)} showings from ShowMojo")
        
        # DEBUG: Print first showing to verify data structure
        if showings:
            print(f"🔍 DEBUG - First showing data:")
            print(json.dumps(showings[0], indent=2))
        
        # Build payload for Lovable
        payload = {
            "sync_timestamp": showings_data.get("sync_timestamp"),
            "days_back": request.days_back,
            "total_showings": len(showings),
            "showings": showings
        }
        
        # DEBUG: Print webhook URL and payload summary
        print(f"🔍 DEBUG - Webhook URL: {LOVABLE_SHOWINGS_WEBHOOK}")
        print(f"🔍 DEBUG - Payload summary: {len(showings)} showings, timestamp: {payload['sync_timestamp']}")
        if len(showings) > 0:
            print(f"🔍 DEBUG - First 3 showings:")
            print(json.dumps(showings[:3], indent=2))
        
        # Send to Lovable webhook
        print("📤 Sending to webhook...")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                LOVABLE_SHOWINGS_WEBHOOK,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {LOVABLE_AUTH_TOKEN}"
                },
                timeout=60.0
            )
            
            print(f"📥 Webhook response status: {response.status_code}")
            print(f"📥 Webhook response body: {response.text[:500]}")
            
            if response.status_code == 200:
                print(f"✅ Showing data sent to Lovable successfully: {len(showings)} showings")
            else:
                print(f"❌ Failed to send to Lovable: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"❌ Error in ShowMojo sync: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

# ============================================================================
# END OF FILE - IF YOU SEE THIS LINE, THE FILE IS COMPLETE
# ============================================================================
