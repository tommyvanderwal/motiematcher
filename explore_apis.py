"""
API Explorer voor Nederlandse Overheid APIs
Test echte API calls naar officielebekendmakingen.nl en tweedekamer.nl
"""

import requests
import json
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DutchParliamentAPIExplorer:
    """Explore real Dutch parliament APIs to understand data structure"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MotieMatcher-APIExplorer/1.0',
            'Accept': 'application/json'
        })
    
    def explore_officielebekendmakingen_api(self):
        """Test officielebekendmakingen.nl API"""
        logger.info("=== Exploring officielebekendmakingen.nl API ===")
        
        base_url = "https://zoek.officielebekendmakingen.nl"
        
        # Try different endpoints
        endpoints_to_test = [
            "/api/v1/",
            "/api/",
            "/zoeken/api/",
            "/sru/Search",  # SRU is a common format for Dutch gov APIs
        ]
        
        for endpoint in endpoints_to_test:
            try:
                url = f"{base_url}{endpoint}"
                logger.info(f"Testing endpoint: {url}")
                
                response = self.session.get(url, timeout=10)
                logger.info(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    logger.info(f"Content-Type: {response.headers.get('content-type')}")
                    content = response.text[:500]  # First 500 chars
                    logger.info(f"Response preview: {content}")
                    
                    # Save full response
                    with open(f'output/api_response_bekendmakingen_{endpoint.replace("/", "_")}.txt', 'w', encoding='utf-8') as f:
                        f.write(f"URL: {url}\n")
                        f.write(f"Status: {response.status_code}\n")
                        f.write(f"Headers: {dict(response.headers)}\n\n")
                        f.write(response.text)
                
            except Exception as e:
                logger.error(f"Error testing {endpoint}: {e}")
        
        # Try SRU search for recent laws
        try:
            sru_url = f"{base_url}/sru/Search"
            params = {
                'query': 'type=wet AND date>=2024-01-01',
                'maximumRecords': 5,
                'recordSchema': 'gzd'
            }
            
            logger.info(f"Testing SRU search: {sru_url}")
            response = self.session.get(sru_url, params=params, timeout=15)
            logger.info(f"SRU Status: {response.status_code}")
            
            if response.status_code == 200:
                with open('output/api_response_sru_search.xml', 'w', encoding='utf-8') as f:
                    f.write(f"URL: {sru_url}\n")
                    f.write(f"Params: {params}\n\n")
                    f.write(response.text)
                logger.info("SRU response saved to output/api_response_sru_search.xml")
                
        except Exception as e:
            logger.error(f"SRU search error: {e}")
    
    def explore_tweedekamer_api(self):
        """Test Tweede Kamer OpenData API"""
        logger.info("=== Exploring Tweede Kamer OpenData API ===")
        
        base_url = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"
        
        # Test main endpoints
        endpoints_to_test = [
            "/",
            "/Activiteit",  # Activities/motions
            "/Besluit",     # Decisions
            "/Document",    # Documents
            "/Stemming",    # Voting
            "/Persoon",     # Persons/MPs
            "/Fractie"      # Parliamentary groups/parties
        ]
        
        for endpoint in endpoints_to_test:
            try:
                url = f"{base_url}{endpoint}"
                params = {'$top': 3, '$orderby': 'Id desc'} if endpoint != "/" else {}
                
                logger.info(f"Testing endpoint: {url}")
                
                response = self.session.get(url, params=params, timeout=15)
                logger.info(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    logger.info(f"Content-Type: {response.headers.get('content-type')}")
                    
                    # Try to parse JSON
                    try:
                        data = response.json()
                        logger.info(f"JSON keys: {list(data.keys()) if isinstance(data, dict) else 'List/Other'}")
                        
                        # Save response
                        filename = f'output/api_response_tk_{endpoint.replace("/", "_")}.json'
                        with open(filename, 'w', encoding='utf-8') as f:
                            json.dump({
                                'url': url,
                                'params': params,
                                'status': response.status_code,
                                'headers': dict(response.headers),
                                'data': data
                            }, f, indent=2, ensure_ascii=False)
                        
                        logger.info(f"Response saved to {filename}")
                        
                    except json.JSONDecodeError:
                        # Not JSON, save as text
                        filename = f'output/api_response_tk_{endpoint.replace("/", "_")}.txt'
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(f"URL: {url}\n")
                            f.write(f"Status: {response.status_code}\n\n")
                            f.write(response.text[:2000])  # First 2000 chars
                        logger.info(f"Text response saved to {filename}")
                
            except Exception as e:
                logger.error(f"Error testing {endpoint}: {e}")
    
    def search_for_recent_motions(self):
        """Search for recent motions specifically"""
        logger.info("=== Searching for Recent Motions ===")
        
        tk_base = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"
        
        # Search for motions (Activiteit with specific types)
        try:
            url = f"{tk_base}/Activiteit"
            params = {
                '$filter': "contains(Onderwerp, 'motie') or contains(Soort, 'motie')",
                '$top': 5,
                '$orderby': 'Datum desc',
                '$expand': 'Besluit,Document'
            }
            
            logger.info(f"Searching for motions: {url}")
            response = self.session.get(url, params=params, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                
                with open('output/api_motions_search.json', 'w', encoding='utf-8') as f:
                    json.dump({
                        'url': url,
                        'params': params,
                        'response': data
                    }, f, indent=2, ensure_ascii=False)
                
                logger.info("Motion search results saved to output/api_motions_search.json")
                
                # Log summary
                if 'value' in data and data['value']:
                    logger.info(f"Found {len(data['value'])} activities")
                    for item in data['value'][:2]:  # Show first 2
                        logger.info(f"- {item.get('Onderwerp', 'No subject')[:100]}")
            
        except Exception as e:
            logger.error(f"Motion search error: {e}")
    
    def search_for_recent_laws(self):
        """Search for recent laws"""
        logger.info("=== Searching for Recent Laws ===")
        
        # Try officiële bekendmakingen for laws
        try:
            base_url = "https://zoek.officielebekendmakingen.nl"
            
            # Different search approaches
            search_urls = [
                f"{base_url}/zoeken/resultaat/?zkt=Uitgebreid&pst=Staatsblad&vrt=wet&zkd=InDeGeheleDocument&dpr=Alle&spd=20240101&epd=20241231&sdt=DatumBesluit&ap=&pnr=1&rpp=10"
            ]
            
            for url in search_urls:
                logger.info(f"Testing law search: {url}")
                response = self.session.get(url, timeout=15)
                
                if response.status_code == 200:
                    with open('output/api_laws_search.html', 'w', encoding='utf-8') as f:
                        f.write(f"URL: {url}\n\n")
                        f.write(response.text)
                    logger.info("Law search HTML saved")
                    
        except Exception as e:
            logger.error(f"Law search error: {e}")

def main():
    """Main exploration function"""
    explorer = DutchParliamentAPIExplorer()
    
    print("=== Dutch Parliament API Explorer ===")
    print("Testing real APIs to understand data structure...")
    
    # Test Tweede Kamer API first (most likely to work)
    explorer.explore_tweedekamer_api()
    
    # Search for specific content
    explorer.search_for_recent_motions()
    
    # Test Officiële Bekendmakingen
    explorer.explore_officielebekendmakingen_api()
    explorer.search_for_recent_laws()
    
    print("\n✅ API exploration completed!")
    print("Check output/ directory for raw API responses")

if __name__ == "__main__":
    main()