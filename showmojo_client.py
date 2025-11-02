"""
ShowMojo API Client
Fetches showing data from ShowMojo using the Report Export API
"""
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import time


class ShowMojoClient:
    """Client for ShowMojo Report Export API"""
    
    def __init__(self, email: str, password: str):
        """
        Initialize ShowMojo client
        
        Args:
            email: ShowMojo account email
            password: ShowMojo account password
        """
        self.email = email
        self.password = password
        self.base_url = "https://showmojo.com/api/v3"
        self.session = requests.Session()
        self.auth_token = None
    
    def _authenticate(self) -> bool:
        """
        Authenticate with ShowMojo API
        
        Returns:
            bool: True if authentication successful
        """
        try:
            # ShowMojo uses basic auth with email/password
            auth_url = f"{self.base_url}/auth/login"
            response = self.session.post(
                auth_url,
                json={
                    "email": self.email,
                    "password": self.password
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("token")
                return True
            else:
                print(f"ShowMojo authentication failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error authenticating with ShowMojo: {e}")
            return False
    
    def get_showings(self, days_back: int = 30, property_id: Optional[str] = None) -> Dict:
        """
        Fetch showing data from ShowMojo Report Export API
        
        Args:
            days_back: Number of days back to fetch data (default: 30)
            property_id: Optional property ID to filter results
        
        Returns:
            Dict with success status and showing data
        """
        try:
            # Authenticate if not already authenticated
            if not self.auth_token:
                if not self._authenticate():
                    return {
                        "success": False,
                        "error": "Authentication failed",
                        "showings": []
                    }
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Format dates for API (YYYY-MM-DD)
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")
            
            # Build API request
            report_url = f"{self.base_url}/reports/prospect_showing_data"
            params = {
                "start_date": start_date_str,
                "end_date": end_date_str
            }
            
            if property_id:
                params["property_id"] = property_id
            
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            print(f"Fetching ShowMojo data from {start_date_str} to {end_date_str}...")
            
            response = self.session.get(
                report_url,
                params=params,
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                showings = self._parse_showings(data)
                
                return {
                    "success": True,
                    "sync_timestamp": datetime.now().isoformat(),
                    "start_date": start_date_str,
                    "end_date": end_date_str,
                    "showings": showings
                }
            
            elif response.status_code == 401:
                # Token expired, re-authenticate and retry
                print("Token expired, re-authenticating...")
                self.auth_token = None
                if self._authenticate():
                    return self.get_showings(days_back, property_id)
                else:
                    return {
                        "success": False,
                        "error": "Re-authentication failed",
                        "showings": []
                    }
            
            else:
                return {
                    "success": False,
                    "error": f"API request failed: {response.status_code}",
                    "showings": []
                }
        
        except Exception as e:
            print(f"Error fetching ShowMojo data: {e}")
            return {
                "success": False,
                "error": str(e),
                "showings": []
            }
    
    def _parse_showings(self, raw_data: Dict) -> List[Dict]:
        """
        Parse raw ShowMojo API response into structured showing data
        
        Args:
            raw_data: Raw API response data
        
        Returns:
            List of parsed showing records
        """
        showings = []
        
        # ShowMojo returns data in various formats depending on the report
        # This is a generic parser that handles common fields
        
        if isinstance(raw_data, dict):
            # If data has a 'showings' or 'data' key
            showing_list = raw_data.get("showings") or raw_data.get("data") or raw_data.get("results") or []
        elif isinstance(raw_data, list):
            showing_list = raw_data
        else:
            showing_list = []
        
        for item in showing_list:
            showing = {
                "showing_id": item.get("id") or item.get("showing_id"),
                "property_id": item.get("property_id"),
                "property_address": item.get("property_address") or item.get("address"),
                "prospect_name": item.get("prospect_name") or item.get("name"),
                "prospect_email": item.get("prospect_email") or item.get("email"),
                "prospect_phone": item.get("prospect_phone") or item.get("phone"),
                "showing_date": item.get("showing_date") or item.get("date"),
                "showing_time": item.get("showing_time") or item.get("time"),
                "status": item.get("status"),
                "confirmed": item.get("confirmed", False),
                "attended": item.get("attended"),
                "cancelled": item.get("cancelled", False),
                "notes": item.get("notes"),
                "created_at": item.get("created_at"),
                "updated_at": item.get("updated_at")
            }
            
            showings.append(showing)
        
        return showings
    
    def test_connection(self) -> bool:
        """
        Test connection to ShowMojo API
        
        Returns:
            bool: True if connection successful
        """
        try:
            if self._authenticate():
                print("✅ ShowMojo connection successful")
                return True
            else:
                print("❌ ShowMojo connection failed")
                return False
        except Exception as e:
            print(f"❌ ShowMojo connection error: {e}")
            return False


# Test the client if run directly
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    email = os.getenv("SHOWMOJO_EMAIL")
    password = os.getenv("SHOWMOJO_PASSWORD")
    
    if email and password:
        client = ShowMojoClient(email, password)
        
        # Test connection
        if client.test_connection():
            # Fetch last 7 days of showings
            result = client.get_showings(days_back=7)
            
            if result["success"]:
                print(f"\n✅ Retrieved {len(result['showings'])} showings")
                print(f"Date range: {result['start_date']} to {result['end_date']}")
                
                if result["showings"]:
                    print("\nFirst showing:")
                    print(result["showings"][0])
            else:
                print(f"\n❌ Failed to fetch showings: {result['error']}")
    else:
        print("❌ SHOWMOJO_EMAIL and SHOWMOJO_PASSWORD environment variables not set")
