#!/usr/bin/env python3
"""
Re-collect Stemming Data with Complete Fields
Fix the incomplete stemming data collection.
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime

class CompleteStemmingCollector:
    """Re-collect stemming data with all required fields."""

    def __init__(self):
        self.base_url = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MotieMatcher-CompleteDataCollector/1.0',
            'Accept': 'application/json'
        })

    def get_total_count(self):
        """Get total number of stemming records."""
        try:
            url = f"{self.base_url}/Stemming/$count"
            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                return int(response.text)
            else:
                print(f"Count request failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"Count error: {e}")
            return None

    def collect_complete_stemming_data(self, start_page=1, max_pages=None):
        """Collect complete stemming data with all fields."""

        print("🔄 RE-COLLECTING COMPLETE STEMMING DATA")
        print("=" * 50)

        # Create output directory
        output_dir = Path("bronmateriaal-onbewerkt/stemming_complete")
        output_dir.mkdir(exist_ok=True)

        # Get total count
        total_count = self.get_total_count()
        if total_count:
            print(f"Total stemming records available: {total_count}")

        page_size = 250
        page = start_page
        collected = 0

        while True:
            if max_pages and page > max_pages:
                break

            try:
                skip = (page - 1) * page_size
                url = f"{self.base_url}/Stemming?$skip={skip}&$top={page_size}"

                print(f"Collecting page {page} (records {skip+1}-{skip+page_size})...")
                response = self.session.get(url, timeout=60)

                if response.status_code == 200:
                    data = response.json()
                    records = data.get('value', [])

                    if not records:
                        print(f"No more records at page {page}")
                        break

                    # Check if records have required fields
                    if records:
                        sample = records[0]
                        has_besluit_id = 'Besluit_Id' in sample
                        has_persoon_id = 'Persoon_Id' in sample
                        has_fractie_id = 'Fractie_Id' in sample

                        print(f"  Sample record has Besluit_Id: {has_besluit_id}")
                        print(f"  Sample record has Persoon_Id: {has_persoon_id}")
                        print(f"  Sample record has Fractie_Id: {has_fractie_id}")

                        if not (has_besluit_id and has_persoon_id and has_fractie_id):
                            print("  ❌ Required fields missing - data structure issue")
                            break

                    # Save the complete data
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"stemming_page_{page}_complete_{timestamp}.json"
                    filepath = output_dir / filename

                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(records, f, indent=2, ensure_ascii=False)

                    collected += len(records)
                    print(f"  ✅ Saved {len(records)} records to {filename}")

                    # Rate limiting
                    time.sleep(1)

                elif response.status_code == 400:
                    print(f"Bad request at page {page}: {response.text}")
                    break
                else:
                    print(f"Request failed at page {page}: {response.status_code}")
                    break

            except Exception as e:
                print(f"Error at page {page}: {e}")
                break

            page += 1

        print(f"\n✅ Collection complete: {collected} records collected")
        return collected

def main():
    """Main collection function."""
    collector = CompleteStemmingCollector()

    # Test with just a few pages first
    print("Testing with first 2 pages...")
    collected = collector.collect_complete_stemming_data(max_pages=2)

    if collected > 0:
        print("\n✅ Test successful! Complete data collection is working.")
        print("🔄 Run with max_pages=None to collect all data")
    else:
        print("\n❌ Test failed - check API access and data structure")

if __name__ == "__main__":
    main()