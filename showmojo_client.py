"""
ShowMojo API Client
Fetches showing data from ShowMojo using the Report Export API
"""
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
from typing import Optional, Dict, List


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
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # Format dates for API (YYYY-MM-DD)
            start_date_str = start_date.strftime("%Y-%m-%d")
            end_date_str = end_date.strftime("%Y-%m-%d")
            
            # Build API request
            report_url = f"{self.base_url}/reports/prospect_showing_data"
            
            print(f"Fetching ShowMojo data from {start_date_str} to {end_date_str}...")
            
            # ShowMojo uses HTTP Basic Auth directly - no separate login needed!
            response = requests.post(
                report_url,
                auth=HTTPBasicAuth(self.email, self.password),
                data={
                    "start_date": start_date_str,
                    "end_date": end_date_str
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                showings = self._parse_showings(data)
                
                print(f"Successfully retrieved {len(showings)} showings from ShowMojo")
                
                return {
                    "success": True,
                    "sync_timestamp": datetime.now().isoformat(),
                    "start_date": start_date_str,
                    "end_date": end_date_str,
                    "showings": showings
                }
            
            elif response.status_code == 401:
                print(f"ShowMojo authentication failed: Invalid credentials")
                return {
                    "success": False,
                    "error": "Authentication failed - check email/password",
                    "showings": []
                }
            
            else:
                print(f"ShowMojo API error: {response.status_code} - {response.text}")
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
    
    def _parse_showings(self, data: Dict) -> List[Dict]:
        """
        Parse showing data from API response
        
        Args:
            data: Raw API response data
        
        Returns:
            List of parsed showing dictionaries
        """
        showings = []
        
        # ShowMojo returns data in different formats depending on the report
        # Handle both list and dict responses
        if isinstance(data, list):
            showing_list = data
        elif isinstance(data, dict):
            # Try common keys
            showing_list = data.get("data") or data.get("showings") or data.get("results") or []
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
            # Try to fetch last 1 day of data as a test
            result = self.get_showings(days_back=1)
            
            if result.get("success"):
                print("✅ ShowMojo connection successful")
                return True
            else:
                print(f"❌ ShowMojo connection failed: {result.get('error')}")
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
            
            if result.get("success"):
                print(f"\n✅ Retrieved {len(result['showings'])} showings")
                
                # Print first showing as example
                if result['showings']:
                    print("\nExample showing:")
                    print(result['showings'][0])
            else:
                print(f"\n❌ Failed to get showings: {result.get('error')}")
    else:
        print("❌ SHOWMOJO_EMAIL and SHOWMOJO_PASSWORD environment variables not set")
