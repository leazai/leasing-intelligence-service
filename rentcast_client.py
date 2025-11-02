"""
RentCast API Client
Fetches market data and comparable properties
"""
import os
import requests
from typing import Dict, List, Optional
from datetime import datetime


class RentCastClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.rentcast.io/v1"
        self.headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def get_market_data(
        self,
        address: str,
        bedrooms: int,
        bathrooms: float,
        square_footage: int,
        property_type: str = "Single Family",
        radius: float = 0.5
    ) -> Dict:
        """
        Get market analysis data for a listing
        
        Args:
            address: Full property address
            bedrooms: Number of bedrooms
            bathrooms: Number of bathrooms
            square_footage: Property square footage
            property_type: Type of property
            radius: Search radius in miles (default 0.5)
        
        Returns:
            Dict with market analysis data
        """
        try:
            # Get rent estimate
            rent_estimate = self._get_rent_estimate(address)
            
            # Get comparable properties
            comparables = self._get_comparables(
                address, bedrooms, bathrooms, square_footage, property_type, radius
            )
            
            # Calculate market statistics
            market_stats = self._calculate_market_stats(comparables, square_footage)
            
            return {
                "success": True,
                "rent_estimate": rent_estimate,
                "comparables": comparables,
                "market_stats": market_stats,
                "radius": radius
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_rent_estimate(self, address: str) -> Optional[Dict]:
        """Get rent estimate for an address"""
        try:
            endpoint = f"{self.base_url}/avm/rent/long-term"
            params = {"address": address}
            
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"RentCast rent estimate error: {response.status_code} - {response.text}")
                return None
        
        except Exception as e:
            print(f"Error getting rent estimate: {e}")
            return None
    
    def _get_comparables(
        self,
        address: str,
        bedrooms: int,
        bathrooms: float,
        square_footage: int,
        property_type: str,
        radius: float
    ) -> List[Dict]:
        """Get comparable properties"""
        try:
            endpoint = f"{self.base_url}/listings/rental/long-term"
            
            params = {
                "address": address,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "propertyType": property_type,
                "radius": radius,
                "limit": 50
            }
            
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                # Response is a list of listings, not a dict with comparables
                return data if isinstance(data, list) else []
            else:
                print(f"RentCast comparables error: {response.status_code} - {response.text}")
                return []
        
        except Exception as e:
            print(f"Error getting comparables: {e}")
            return []
    
    def _calculate_market_stats(self, comparables: List[Dict], listing_sqft: int) -> Dict:
        """Calculate market statistics from comparables"""
        if not comparables:
            return {
                "market_avg_rent": 0,
                "market_median_rent": 0,
                "market_rent_range_low": 0,
                "market_rent_range_high": 0,
                "market_avg_rent_per_sqft": 0,
                "market_avg_dom": 0,
                "market_median_dom": 0,
                "total_similar_listings": 0,
                "active_listings_count": 0,
                "rented_listings_count": 0,
                "avg_rent_active": 0,
                "avg_rent_rented": 0,
                "avg_rent_per_sqft_active": 0,
                "avg_rent_per_sqft_rented": 0,
                "avg_dom_active": 0,
                "avg_dom_rented": 0
            }
        
        # Separate active and rented listings
        active_listings = [c for c in comparables if c.get("status") in ["Active", "For Rent"]]
        rented_listings = [c for c in comparables if c.get("status") in ["Rented", "Leased"]]
        
        # Extract rents and DOMs
        all_rents = [c.get("price", 0) for c in comparables if c.get("price")]
        all_doms = [c.get("daysOnMarket", 0) for c in comparables if c.get("daysOnMarket")]
        
        active_rents = [c.get("price", 0) for c in active_listings if c.get("price")]
        rented_rents = [c.get("price", 0) for c in rented_listings if c.get("price")]
        
        active_doms = [c.get("daysOnMarket", 0) for c in active_listings if c.get("daysOnMarket")]
        rented_doms = [c.get("daysOnMarket", 0) for c in rented_listings if c.get("daysOnMarket")]
        
        # Calculate averages
        market_avg_rent = sum(all_rents) // len(all_rents) if all_rents else 0
        market_median_rent = sorted(all_rents)[len(all_rents) // 2] if all_rents else 0
        market_avg_dom = sum(all_doms) // len(all_doms) if all_doms else 0
        market_median_dom = sorted(all_doms)[len(all_doms) // 2] if all_doms else 0
        
        avg_rent_active = sum(active_rents) // len(active_rents) if active_rents else 0
        avg_rent_rented = sum(rented_rents) // len(rented_rents) if rented_rents else 0
        
        avg_dom_active = sum(active_doms) // len(active_doms) if active_doms else 0
        avg_dom_rented = sum(rented_doms) // len(rented_doms) if rented_doms else 0
        
        # Calculate rent per sqft
        market_avg_rent_per_sqft = round(market_avg_rent / listing_sqft, 2) if listing_sqft > 0 else 0
        avg_rent_per_sqft_active = round(avg_rent_active / listing_sqft, 2) if listing_sqft > 0 and avg_rent_active > 0 else 0
        avg_rent_per_sqft_rented = round(avg_rent_rented / listing_sqft, 2) if listing_sqft > 0 and avg_rent_rented > 0 else 0
        
        return {
            "market_avg_rent": market_avg_rent,
            "market_median_rent": market_median_rent,
            "market_rent_range_low": min(all_rents) if all_rents else 0,
            "market_rent_range_high": max(all_rents) if all_rents else 0,
            "market_avg_rent_per_sqft": market_avg_rent_per_sqft,
            "market_avg_dom": market_avg_dom,
            "market_median_dom": market_median_dom,
            "total_similar_listings": len(comparables),
            "active_listings_count": len(active_listings),
            "rented_listings_count": len(rented_listings),
            "avg_rent_active": avg_rent_active,
            "avg_rent_rented": avg_rent_rented,
            "avg_rent_per_sqft_active": avg_rent_per_sqft_active,
            "avg_rent_per_sqft_rented": avg_rent_per_sqft_rented,
            "avg_dom_active": avg_dom_active,
            "avg_dom_rented": avg_dom_rented
        }
