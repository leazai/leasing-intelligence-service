"""
Test script for syndication checker
"""
from syndication_checker import SyndicationChecker
import json

# Test with a real property
checker = SyndicationChecker()

print("Testing Syndication Checker")
print("=" * 50)
print("Address: 5500 Grand Lake Dr, San Antonio, TX 78244")
print("=" * 50)

results = checker.check_all_sites(
    address="5500 Grand Lake Dr",
    city="San Antonio",
    state="TX"
)

print(f"\n✅ Syndication Check Complete!")
print(f"Found on {results['total_sites_found']}/27 sites")
print(f"Top 6 sites: {results['top_6_found_count']}/6")
print(f"\nSites Found:")
for site in results['sites_found'][:10]:
    print(f"  ✓ {site}")

print(f"\nSites Not Found:")
for site in results['sites_not_found'][:10]:
    print(f"  ✗ {site}")

print(f"\nTop 6 Sites Status:")
for site, found in results['top_6_sites_status'].items():
    status = "✓" if found else "✗"
    print(f"  {status} {site}")
