"""
Parliamentary Data Scraper for Dutch Parliament
Collects moties, wetten, and amendementen from official sources
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ParliamentaryItem:
    """Represents a motion, law, or amendment"""
    id: str
    type: str  # 'motie', 'wet', 'amendement'
    title: str
    summary: str
    date: str
    proposer: str
    status: str
    text_url: Optional[str] = None
    voting_url: Optional[str] = None
    raw_data: Optional[Dict] = None

class ParliamentaryScraper:
    """Scrapes Dutch parliamentary data from official sources"""
    
    def __init__(self):
        self.base_urls = {
            'officielebekendmakingen': 'https://zoek.officielebekendmakingen.nl/api/v1/',
            'tweedekamer': 'https://opendata.tweedekamer.nl/api/v1/'
        }
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MotieMatcher-ETL/1.0 (contact@example.com)'
        })
    
    def get_recent_motions(self, days_back: int = 365 * 10) -> List[ParliamentaryItem]:
        """
        Retrieve motions from the last specified days
        Default: 10 years (365 * 10 days)
        """
        logger.info(f"Fetching motions from last {days_back} days")
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        motions = []
        
        # Example API call structure - adjust based on actual API documentation
        try:
            params = {
                'type': 'motie',
                'date_from': start_date.strftime('%Y-%m-%d'),
                'date_to': end_date.strftime('%Y-%m-%d'),
                'limit': 1000
            }
            
            # Placeholder for actual API implementation
            # response = self.session.get(self.base_urls['tweedekamer'] + 'documenten', params=params)
            
            # For now, create sample data structure
            sample_motion = ParliamentaryItem(
                id="tk-2024-1234",
                type="motie",
                title="Motie van lid X over klimaatbeleid",
                summary="Een motie betreffende aanscherping van het klimaatbeleid",
                date="2024-03-15",
                proposer="Lid X (Partij Y)",
                status="aangenomen",
                text_url="https://zoek.officielebekendmakingen.nl/kst-12345",
                voting_url="https://opendata.tweedekamer.nl/stemming/12345"
            )
            
            motions.append(sample_motion)
            logger.info(f"Retrieved {len(motions)} motions")
            
        except Exception as e:
            logger.error(f"Error fetching motions: {e}")
        
        return motions
    
    def get_recent_laws(self, days_back: int = 365 * 10) -> List[ParliamentaryItem]:
        """Retrieve laws from the last specified days"""
        logger.info(f"Fetching laws from last {days_back} days")
        
        laws = []
        
        try:
            # Sample law structure
            sample_law = ParliamentaryItem(
                id="wet-2024-5678",
                type="wet",
                title="Wet klimaatakkoord implementatie",
                summary="Wet ter implementatie van het klimaatakkoord",
                date="2024-05-20",
                proposer="Minister van Klimaat",
                status="aangenomen",
                text_url="https://zoek.officielebekendmakingen.nl/stb-2024-123"
            )
            
            laws.append(sample_law)
            logger.info(f"Retrieved {len(laws)} laws")
            
        except Exception as e:
            logger.error(f"Error fetching laws: {e}")
        
        return laws
    
    def get_recent_amendments(self, days_back: int = 365 * 10) -> List[ParliamentaryItem]:
        """Retrieve amendments from the last specified days"""
        logger.info(f"Fetching amendments from last {days_back} days")
        
        amendments = []
        
        try:
            # Sample amendment structure
            sample_amendment = ParliamentaryItem(
                id="amend-2024-9012",
                type="amendement",
                title="Amendement-X op wetsvoorstel Y",
                summary="Amendement ter uitbreiding van de bepalingen",
                date="2024-04-10",
                proposer="Lid Z (Partij W)",
                status="verworpen"
            )
            
            amendments.append(sample_amendment)
            logger.info(f"Retrieved {len(amendments)} amendments")
            
        except Exception as e:
            logger.error(f"Error fetching amendments: {e}")
        
        return amendments
    
    def collect_all_data(self, pilot_mode: bool = True) -> List[ParliamentaryItem]:
        """
        Collect all parliamentary data (motions, laws, amendments)
        
        Args:
            pilot_mode: If True, collect limited data for testing (200 items)
        """
        logger.info(f"Starting data collection (pilot_mode: {pilot_mode})")
        
        all_items = []
        
        # Collect different types of parliamentary items
        motions = self.get_recent_motions()
        laws = self.get_recent_laws()
        amendments = self.get_recent_amendments()
        
        all_items.extend(motions)
        all_items.extend(laws)
        all_items.extend(amendments)
        
        # Sort by date (most recent first)
        all_items.sort(key=lambda x: x.date, reverse=True)
        
        if pilot_mode:
            # Limit to 200 items for pilot, ensure we have a mix of types
            motions_sample = [item for item in all_items if item.type == 'motie'][:100]
            laws_sample = [item for item in all_items if item.type == 'wet'][:50]
            amendments_sample = [item for item in all_items if item.type == 'amendement'][:50]
            
            all_items = motions_sample + laws_sample + amendments_sample
            all_items = all_items[:200]  # Ensure max 200 items
        
        logger.info(f"Collected {len(all_items)} total items")
        return all_items

def main():
    """Main execution function"""
    scraper = ParliamentaryScraper()
    
    # Collect data in pilot mode
    items = scraper.collect_all_data(pilot_mode=True)
    
    # Save to JSON for processing
    output_data = []
    for item in items:
        output_data.append({
            'id': item.id,
            'type': item.type,
            'title': item.title,
            'summary': item.summary,
            'date': item.date,
            'proposer': item.proposer,
            'status': item.status,
            'text_url': item.text_url,
            'voting_url': item.voting_url
        })
    
    # Write to output directory
    with open('output/raw_parliamentary_data.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Saved {len(output_data)} items to output/raw_parliamentary_data.json")

if __name__ == "__main__":
    main()