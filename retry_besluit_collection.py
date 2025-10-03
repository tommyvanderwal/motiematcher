#!/usr/bin/env python3
"""
Retry besluit collection from page 67 onwards to fix 500 error
"""

import requests
import json
import os
import time
from datetime import datetime
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BesluitRetryCollector:
    def __init__(self, base_dir="bronmateriaal-onbewerkt"):
        self.base_url = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"
        self.base_dir = Path(base_dir)
        self.parliament_start = datetime(2023, 12, 6)

    def clean_for_json(self, obj):
        """Maak object JSON-serializable"""
        if isinstance(obj, dict):
            return {k: self.clean_for_json(v) for k, v in obj.items() if not k.endswith('_Id') or k == 'Id'}
        elif isinstance(obj, list):
            return [self.clean_for_json(item) for item in obj]
        else:
            return obj

    def save_raw_response(self, entity_type, filename_prefix, data, timespan):
        """Sla ruwe API response op"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timespan}_{timestamp}.json"
        filepath = self.base_dir / entity_type.lower() / filename

        clean_data = self.clean_for_json(data)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(clean_data, f, indent=2, ensure_ascii=False)

        file_size = filepath.stat().st_size
        logger.info(f"💾 Saved: {filepath.name} ({file_size/1024:.1f} KB)")

        return filepath

    def collect_besluit_from_page(self, start_page=67):
        """Verzamel besluit data vanaf specifieke pagina"""
        logger.info(f"\n🏛️ RETRYING BESLUIT COLLECTION from page {start_page}")
        logger.info("=" * 60)

        all_records = []
        skip = (start_page - 1) * 250  # OData pagination
        page = start_page

        while True:
            logger.info(f"📄 Page {page} (skip {skip})...")

            try:
                url = f"{self.base_url}/Besluit?$skip={skip}&$orderby=GewijzigdOp desc"
                response = requests.get(url, timeout=30)

                if response.status_code == 200:
                    data = response.json()

                    if 'value' in data:
                        records = data['value']
                    else:
                        records = data if isinstance(data, list) else []

                    logger.info(f"  📊 Retrieved {len(records)} records")

                    if len(records) == 0:
                        logger.info(f"  ✅ No more records found")
                        break

                    # Filter by date (vanaf december 2023)
                    recent_records = []
                    old_count = 0

                    for record in records:
                        record_date_str = record.get('GewijzigdOp', '')
                        if record_date_str:
                            try:
                                record_date = datetime.fromisoformat(record_date_str.replace('Z', '+00:00'))
                                if record_date.replace(tzinfo=None) >= self.parliament_start:
                                    recent_records.append(record)
                                else:
                                    old_count += 1
                            except:
                                # Als datum parsing faalt, neem record mee (safety)
                                recent_records.append(record)

                    if old_count > 0:
                        logger.info(f"  🛑 Found {old_count} records older than Dec 6, 2023")
                        if len(recent_records) == 0:
                            logger.info(f"  ✅ Reached end of parliamentary term data")
                            break

                    all_records.extend(recent_records)

                    # Save page als we relevante data hebben
                    if recent_records:
                        self.save_raw_response(
                            'besluit',
                            f'besluit_page_{page}',
                            recent_records,
                            'retry'
                        )

                    # Check of we alle data hebben (minder dan 250 = einde API)
                    if len(records) < 250:
                        logger.info(f"  ✅ Got {len(records)} records (less than 250), end of API data")
                        break

                    skip += 250
                    page += 1
                    time.sleep(1)  # API vriendelijk

                else:
                    logger.error(f"  ❌ Error fetching page {page}: {response.status_code}")
                    if response.status_code == 500:
                        logger.error("  🔴 500 Internal Server Error - API issue")
                        # Try once more after longer wait
                        time.sleep(5)
                        response = requests.get(url, timeout=30)
                        if response.status_code == 200:
                            logger.info("  ✅ Retry successful!")
                            continue
                        else:
                            logger.error(f"  ❌ Retry also failed: {response.status_code}")
                    break

            except Exception as e:
                logger.error(f"  ❌ Exception on page {page}: {e}")
                break

        logger.info(f"✅ Besluit retry: {len(all_records)} additional records collected")
        return all_records

if __name__ == "__main__":
    collector = BesluitRetryCollector()

    print("🔄 BESLUIT COLLECTION RETRY")
    print("=" * 40)
    print("Starting from page 67 to fix 500 error")
    print()

    records = collector.collect_besluit_from_page(start_page=67)

    print(f"\n🎉 SUCCESS!")
    print(f"Collected {len(records)} additional besluit records")
    print("Check bronmateriaal-onbewerkt/besluit/ for new files")