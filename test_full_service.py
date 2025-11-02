"""
Full service integration test
Tests both market analysis and syndication check endpoints
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

print("=" * 70)
print("LEASING INTELLIGENCE SERVICE - FULL INTEGRATION TEST")
print("=" * 70)

# Test 1: Health Check
print("\n1. Testing Health Check...")
response = requests.get(f"{BASE_URL}/")
print(f"   Status: {response.status_code}")
print(f"   Response: {json.dumps(response.json(), indent=2)}")

# Test 2: Market Analysis
print("\n2. Testing Market Analysis Endpoint...")
market_request = {
    "listing_id": "test-listing-001",
    "address": "5500 Grand Lake Dr",
    "city": "San Antonio",
    "state": "TX",
    "bedrooms": 3,
    "bathrooms": 2.0,
    "square_footage": 1500,
    "current_rent": 1650,
    "days_on_market": 25,
    "property_type": "Single Family",
    "radius": 0.5
}

print(f"   Request: {json.dumps(market_request, indent=2)}")
response = requests.post(f"{BASE_URL}/analyze-market", json=market_request)
print(f"   Status: {response.status_code}")
print(f"   Response: {json.dumps(response.json(), indent=2)}")

# Test 3: Syndication Check
print("\n3. Testing Syndication Check Endpoint...")
syndication_request = {
    "listing_id": "test-listing-001",
    "address": "5500 Grand Lake Dr",
    "city": "San Antonio",
    "state": "TX",
    "title": "Beautiful 3BR/2BA Home in San Antonio",
    "description": "Spacious 3 bedroom, 2 bathroom home with modern amenities. Features include updated kitchen, large backyard, and 2-car garage. Close to schools and shopping.",
    "price": 1650,
    "bedrooms": 3,
    "bathrooms": 2.0,
    "square_footage": 1500,
    "amenities": ["Pool", "Garage", "Backyard", "Updated Kitchen", "Washer/Dryer"],
    "photos_count": 18
}

print(f"   Request: {json.dumps(syndication_request, indent=2)}")
response = requests.post(f"{BASE_URL}/check-syndication", json=syndication_request)
print(f"   Status: {response.status_code}")
print(f"   Response: {json.dumps(response.json(), indent=2)}")

print("\n" + "=" * 70)
print("✅ ALL TESTS COMPLETED")
print("=" * 70)
print("\nNote: Background tasks are processing. Check server.log for details.")
print("Wait 10-15 seconds, then check the log file:")
print("  tail -50 server.log")
