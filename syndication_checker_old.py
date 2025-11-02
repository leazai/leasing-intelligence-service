"""
Syndication Checker
Searches 27 rental syndication sites to verify listing presence
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, List
from urllib.parse import quote
import time


class SyndicationChecker:
    def __init__(self):
        self.sites = {
            # Top 6 Priority Sites
            "Zillow": "https://www.zillow.com/homes/{address}_rb/",
            "Zumper": "https://www.zumper.com/apartments-for-rent/{city}-{state}",
            "HotPads": "https://hotpads.com/{city}-{state}/apartments-for-rent",
            "Realtor.com": "https://www.realtor.com/realestateandhomes-search/{city}_{state}",
            "Redfin": "https://www.redfin.com/{state}/{city}",
            "Trulia": "https://www.trulia.com/{state}/{city}/",
            
            # Other 21 Sites
            "Apartments.com": "https://www.apartments.com/{city}-{state}/",
            "Rent.com": "https://www.rent.com/{state}/{city}",
            "Rentable": "https://www.rentable.co/{state}/{city}",
            "ApartmentAdvisor": "https://www.apartmentadvisor.com/{state}/{city}",
            "ApartmentPicks": "https://www.apartmentpicks.com/{state}/{city}",
            "Call It Home": "https://www.callithome.com/{state}/{city}",
            "ClaZ.org": "https://www.claz.org/{state}/{city}",
            "College House": "https://www.collegehouse.com/{state}/{city}",
            "CollegePads": "https://www.collegepads.com/{state}/{city}",
            "Diggz": "https://www.diggz.co/{state}/{city}",
            "Domu": "https://www.domu.com/{state}/{city}",
            "Listanza": "https://www.listanza.com/{state}/{city}",
            "Locanto": "https://www.locanto.com/{state}/{city}",
            "Mapliv": "https://www.mapliv.com/{state}/{city}",
            "Mitula": "https://homes.mitula.com/searchRental/{city}-{state}",
            "RentalAds.com": "https://www.rentalads.com/{state}/{city}",
            "Rental Beast": "https://www.rentalbeast.com/{state}/{city}",
            "Rentals.com": "https://www.rentals.com/{state}/{city}",
            "RentalSource": "https://www.rentalsource.com/{state}/{city}",
            "RentDigs": "https://www.rentdigs.com/{state}/{city}",
            "RentHop": "https://www.renthop.com/{state}/{city}",
            "Rentler": "https://www.rentler.com/{state}/{city}",
            "Trovit": "https://realestate.trovit.com/for-rent/{city}-{state}"
        }
        
        self.top_6 = ["Zillow", "Zumper", "HotPads", "Realtor.com", "Redfin", "Trulia"]
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def check_all_sites(self, address: str, city: str, state: str) -> Dict:
        """
        Check if listing appears on all 27 syndication sites
        
        Args:
            address: Property address (e.g., "10224 Olivia Dr")
            city: City name (e.g., "McKinney")
            state: State abbreviation (e.g., "TX")
        
        Returns:
            Dict with syndication status
        """
        sites_found = []
        sites_not_found = []
        site_details = {}
        
        # Check top 6 sites first
        for site_name in self.top_6:
            found, url = self._check_site(site_name, address, city, state)
            if found:
                sites_found.append(site_name)
                site_details[site_name] = {"found": True, "url": url}
            else:
                sites_not_found.append(site_name)
                site_details[site_name] = {"found": False, "url": url}
            
            time.sleep(0.5)  # Rate limiting
        
        # Check remaining sites
        for site_name in self.sites.keys():
            if site_name not in self.top_6:
                found, url = self._check_site(site_name, address, city, state)
                if found:
                    sites_found.append(site_name)
                    site_details[site_name] = {"found": True, "url": url}
                else:
                    sites_not_found.append(site_name)
                    site_details[site_name] = {"found": False, "url": url}
                
                time.sleep(0.5)  # Rate limiting
        
        top_6_found_count = len([s for s in sites_found if s in self.top_6])
        
        return {
            "total_sites_checked": 27,
            "total_sites_found": len(sites_found),
            "sites_found": sites_found,
            "sites_not_found": sites_not_found,
            "top_6_found_count": top_6_found_count,
            "site_details": site_details
        }
    
    def _check_site(self, site_name: str, address: str, city: str, state: str) -> tuple:
        """
        Check if listing is on a specific site
        
        Returns:
            (found: bool, url: str)
        """
        try:
            url_template = self.sites.get(site_name, "")
            
            # Format URL
            url = url_template.format(
                address=quote(address),
                city=city.lower().replace(" ", "-"),
                state=state.lower()
            )
            
            # Make request
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                # Check if address appears in page content
                content = response.text.lower()
                address_clean = address.lower().replace(" ", "")
                
                # Simple check: if address appears in content
                if address_clean in content.replace(" ", ""):
                    return (True, url)
            
            return (False, url)
        
        except Exception as e:
            print(f"Error checking {site_name}: {e}")
            return (False, url if 'url' in locals() else "")
