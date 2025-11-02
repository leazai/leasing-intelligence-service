"""
OpenAI SEO Analyzer
Generates SEO recommendations for rental listings using OpenAI GPT-4
"""
from openai import OpenAI
from typing import Dict, List
import json


class OpenAIAnalyzer:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4.1-mini"  # Supported model
    
    def analyze_listing_seo(
        self,
        address: str,
        title: str,
        description: str,
        price: int,
        bedrooms: int,
        bathrooms: float,
        square_footage: int,
        amenities: List[str],
        photos_count: int,
        syndication_results: Dict,
        market_data: Dict
    ) -> Dict:
        """
        Generate SEO recommendations for a listing
        
        Returns:
            Dict with SEO analysis and recommendations
        """
        try:
            # Build context for AI
            context = self._build_context(
                address, title, description, price, bedrooms, bathrooms,
                square_footage, amenities, photos_count, syndication_results, market_data
            )
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            result = json.loads(response.choices[0].message.content)
            
            return {
                "success": True,
                **result
            }
        
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "overall_seo_score": 50,
                "quick_wins": ["Error generating recommendations"],
                "high_priority_actions": [],
                "site_specific_tips": {}
            }
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for OpenAI"""
        return """You are an expert SEO analyst specializing in rental property listings. 
Your job is to analyze rental listings and provide actionable SEO recommendations to improve visibility on major rental sites like Zillow, Zumper, HotPads, Realtor.com, Redfin, and Trulia.

You must respond with a JSON object containing:
{
  "overall_seo_score": 0-100,
  "quick_wins": ["action 1", "action 2", "action 3"],
  "high_priority_actions": ["action 1", "action 2", "action 3"],
  "site_specific_tips": {
    "Zillow": ["tip 1", "tip 2"],
    "Zumper": ["tip 1", "tip 2"],
    "HotPads": ["tip 1", "tip 2"],
    "Realtor.com": ["tip 1", "tip 2"],
    "Redfin": ["tip 1", "tip 2"],
    "Trulia": ["tip 1", "tip 2"]
  },
  "site_scores": {
    "Zillow": 0-100,
    "Zumper": 0-100,
    "HotPads": 0-100,
    "Realtor.com": 0-100,
    "Redfin": 0-100,
    "Trulia": 0-100
  }
}

Quick wins should be actions that take less than 30 minutes.
High priority actions should have the biggest impact on visibility.
Site-specific tips should be tailored to each platform's ranking algorithm.
Site scores should reflect how well optimized the listing is for each specific site."""
    
    def _build_context(
        self,
        address: str,
        title: str,
        description: str,
        price: int,
        bedrooms: int,
        bathrooms: float,
        square_footage: int,
        amenities: List[str],
        photos_count: int,
        syndication_results: Dict,
        market_data: Dict
    ) -> str:
        """Build context string for OpenAI"""
        
        # Calculate market positioning
        market_avg_rent = market_data.get("market_stats", {}).get("market_avg_rent", 0)
        rent_vs_market = ((price - market_avg_rent) / market_avg_rent * 100) if market_avg_rent > 0 else 0
        
        context = f"""Analyze this rental listing for SEO optimization:

LISTING DETAILS:
- Address: {address}
- Title: {title}
- Description: {description[:500]}... (truncated)
- Price: ${price}/month
- Bedrooms: {bedrooms}
- Bathrooms: {bathrooms}
- Square Footage: {square_footage} sq ft
- Price per sq ft: ${round(price / square_footage, 2) if square_footage > 0 else 0}
- Amenities: {', '.join(amenities[:10])}
- Photos: {photos_count}

SYNDICATION STATUS:
- Found on {syndication_results.get('total_sites_found', 0)}/27 sites
- Top 6 sites: {syndication_results.get('top_6_found_count', 0)}/6 found
- Missing from: {', '.join(syndication_results.get('sites_not_found', [])[:5])}

MARKET ANALYSIS:
- Market average rent: ${market_avg_rent}
- Your rent vs market: {rent_vs_market:+.1f}%
- Market average DOM: {market_data.get('market_stats', {}).get('market_avg_dom', 0)} days
- Similar listings: {market_data.get('market_stats', {}).get('total_similar_listings', 0)}

Provide SEO recommendations focusing on:
1. Quick wins (< 30 min) to improve visibility immediately
2. High priority actions with biggest impact
3. Site-specific optimization for Zillow, Zumper, HotPads, Realtor.com, Redfin, Trulia
4. SEO scores for each site (0-100)

Consider:
- Photo quality and quantity (Zillow loves 15+ photos)
- Title optimization (keywords, location, amenities)
- Description length and quality (250+ words performs better)
- Pricing strategy vs market
- Amenity highlighting
- Freshness (recent updates boost rankings)"""
        
        return context
