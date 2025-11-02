"""
Test script for market analysis endpoint
"""
import requests
import json
import time

# Test data - sample listing
test_listing = {
    "listing_id": "test-001",
    "address": "123 Main Street",
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

print("Testing Market Analysis Endpoint")
print("=" * 50)
print(f"Listing: {test_listing['address']}, {test_listing['city']}, {test_listing['state']}")
print(f"Bedrooms: {test_listing['bedrooms']}, Bathrooms: {test_listing['bathrooms']}")
print(f"Square Footage: {test_listing['square_footage']}")
print(f"Current Rent: ${test_listing['current_rent']}/month")
print(f"Days on Market: {test_listing['days_on_market']}")
print("=" * 50)

# Send request
response = requests.post(
    "http://localhost:8000/analyze-market",
    json=test_listing
)

print(f"\nResponse Status: {response.status_code}")
print(f"Response Body:")
print(json.dumps(response.json(), indent=2))

print("\n✅ Request accepted! Processing in background...")
print("Check server.log for processing details")
