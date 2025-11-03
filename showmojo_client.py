"""
ShowMojo API Client with Debug Logging
Fetches showing data from ShowMojo using the Report Export API
"""
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import json


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
            print(f"API URL: {report_url}")
            
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
            
            print(f"ShowMojo API Response Status: {response.status_code}")
            
            if response.status_code == 200:
                # DEBUG: Print raw response
                raw_response = response.text
                print(f"ShowMojo Raw Response (first 500 chars): {raw_response[:500]}")
                
                try:
                    data = response.json()
                    print(f"ShowMojo Response Type: {type(data)}")
                    
                    # DEBUG: Print response structure
                    if isinstance(data, dict):
                        print(f"ShowMojo Response Keys: {list(data.keys())}")
                    elif isinstance(data, list):
                        print(f"ShowMojo Response is a list with {len(data)} items")
                        if len(data) > 0:
                            print(f"First item keys: {list(data[0].keys()) if isinstance(data[0], dict) else 'Not a dict'}")
                    
                    # DEBUG: Print full response (be careful with large responses)
                    print(f"ShowMojo Full Response: {json.dumps(data, indent=2)[:1000]}")
                    
                except json.JSONDecodeError as e:
                    print(f"ShowMojo Response is not JSON: {e}")
                    print(f"Raw response: {raw_response}")
                    return {
                        "success": False,
                        "error": "Invalid JSON response from ShowMojo",
                        "showings": []
                    }
                
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
                print(f"ShowMojo API error: {response.status_code}")
                print(f"Response text: {response.text[:500]}")
                return {
                    "success": False,
                    "error": f"API request failed: {response.status_code}",
                    "showings": []
                }
        
        except Exception as e:
            print(f"Error fetching ShowMojo data: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
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
        
        print(f"Parsing ShowMojo data...")
        
        # ShowMojo returns data in this format:
        # {"response": {"status": "success", "data": [...]}}
        
        if isinstance(data, list):
            showing_list = data
            print(f"Data is a list with {len(showing_list)} items")
        elif isinstance(data, dict):
            # ShowMojo wraps data in a 'response' object
            if 'response' in data:
                response_obj = data['response']
                if isinstance(response_obj, dict) and 'data' in response_obj:
                    showing_list = response_obj['data']
                    print(f"Extracted {len(showing_list)} items from response.data")
                else:
                    showing_list = []
                    print(f"'response' exists but no 'data' key found")
            else:
                # Try common keys at top level
                showing_list = (
                    data.get("data") or 
                    data.get("showings") or 
                    data.get("results") or 
                    data.get("rows") or
                    data.get("report_data") or
                    []
                )
                print(f"No 'response' key, extracted {len(showing_list)} items using key search")
                
                # If still empty, try to find any list in the dict
                if not showing_list:
                    for key, value in data.items():
                        if isinstance(value, list) and len(value) > 0:
                            showing_list = value
                            print(f"Found list in key '{key}' with {len(showing_list)} items")
                            break
        else:
            showing_list = []
            print(f"Data is neither list nor dict: {type(data)}")
        
        print(f"Processing {len(showing_list)} items...")
        
        for idx, item in enumerate(showing_list):
            if not isinstance(item, dict):
                print(f"Item {idx} is not a dict: {type(item)}")
                continue
                
            # DEBUG: Print first item structure
            if idx == 0:
                print(f"First item structure: {json.dumps(item, indent=2)[:500]}")
            
            showing = {
                "showing_id": item.get("id") or item.get("showing_id") or f"showing_{idx}",
                "property_id": item.get("listing_uid") or item.get("property_id") or item.get("listing_id"),
                "property_address": item.get("showing_address_and_unit") or item.get("property_address") or item.get("address"),
                "prospect_name": item.get("name") or item.get("prospect_name") or item.get("contact_name"),
                "prospect_email": item.get("email") or item.get("prospect_email") or item.get("contact_email"),
                "prospect_phone": item.get("phone") or item.get("prospect_phone") or item.get("contact_phone"),
                "showing_date": item.get("showtime") or item.get("showing_date") or item.get("date") or item.get("scheduled_date"),
                "showing_time": item.get("showtime") or item.get("showing_time") or item.get("time") or item.get("scheduled_time"),
                "status": item.get("status") or "unknown",
                "confirmed": item.get("confirmed", False),
                "attended": item.get("attended"),
                "cancelled": item.get("cancelled", False),
                "notes": item.get("notes") or item.get("comments"),
                "created_at": item.get("created_at") or item.get("created"),
                "updated_at": item.get("updated_at") or item.get("updated")
            }
            
            showings.append(showing)
        
        print(f"Parsed {len(showings)} showings")
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
                    print(json.dumps(result['showings'][0], indent=2))
            else:
                print(f"\n❌ Failed to get showings: {result.get('error')}")
    else:
        print("❌ SHOWMOJO_EMAIL and SHOWMOJO_PASSWORD environment variables not set")
