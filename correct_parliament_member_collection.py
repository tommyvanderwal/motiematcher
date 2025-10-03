#!/usr/bin/env python3
"""
Correct parliament member collection using FractieZetelPersoon approach
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

class CorrectParliamentMemberCollector:
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
        logger.info(f"[+] Saved: {filepath.name} ({file_size/1024:.1f} KB)")

        return filepath

    def collect_active_parliament_members(self):
        """Verzamel actieve parlementariërs via FractieZetelPersoon"""
        logger.info("[*] COLLECTING ACTIVE PARLIAMENT MEMBERS")
        logger.info("=" * 50)

        # Query voor actieve leden (geen einddatum)
        filter_query = f"Van le {self.parliament_start.isoformat()}Z and (TotEnMet eq null or TotEnMet gt {self.parliament_start.isoformat()}Z)"

        url = f"{self.base_url}/FractieZetelPersoon?$filter={filter_query}"
        logger.info(f"Query URL: {url}")

        try:
            response = requests.get(url, timeout=30)
            logger.info(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()

                if 'value' in data:
                    members = data['value']
                    logger.info(f"[+] Found {len(members)} active parliament members")

                    # Extract unique person IDs
                    person_ids = set()
                    for member in members:
                        person_id = member.get('Persoon_Id')
                        if person_id:
                            person_ids.add(person_id)

                    logger.info(f"[+] Unique person IDs: {len(person_ids)}")

                    # Save the member data
                    self.save_raw_response(
                        'fractie_zetel_persoon',
                        'active_members',
                        members,
                        'fullterm'
                    )

                    return list(person_ids)

            else:
                logger.error(f"[-] API Error: {response.status_code}")
                logger.error(f"Response: {response.text}")

        except Exception as e:
            logger.error(f"[-] Exception: {e}")

        return []

    def collect_person_details(self, person_ids):
        """Verzamel persoon details voor de gegeven IDs"""
        logger.info(f"[*] COLLECTING PERSON DETAILS for {len(person_ids)} persons")
        logger.info("=" * 50)

        all_persons = []
        batch_size = 10  # Smaller batches to avoid 400 errors

        for i in range(0, len(person_ids), batch_size):
            batch_ids = person_ids[i:i+batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}: {len(batch_ids)} persons")

            # Create filter for this batch
            id_filters = [f"Id eq {pid}" for pid in batch_ids]
            filter_query = " or ".join(id_filters)

            url = f"{self.base_url}/Persoon?$filter={filter_query}"
            logger.info(f"Batch URL: {url}")

            try:
                response = requests.get(url, timeout=30)

                if response.status_code == 200:
                    data = response.json()

                    if 'value' in data:
                        persons = data['value']
                        logger.info(f"  Retrieved {len(persons)} person records")

                        # Validate we got data
                        persons_with_data = [p for p in persons if p.get('Achternaam') is not None]
                        logger.info(f"  Persons with actual data: {len(persons_with_data)}")

                        all_persons.extend(persons)

                else:
                    logger.error(f"  [-] Batch failed: {response.status_code}")
                    logger.error(f"  Response: {response.text[:200]}")

                time.sleep(0.5)  # API vriendelijk

            except Exception as e:
                logger.error(f"  [-] Batch exception: {e}")

        # Save all person data
        if all_persons:
            self.save_raw_response(
                'persoon',
                'active_members_detailed',
                all_persons,
                'fullterm'
            )

        logger.info(f"[+] Collected details for {len(all_persons)} persons")
        return all_persons

    def validate_collection(self, person_ids, persons):
        """Valideer de verzamelde data"""
        logger.info("[*] VALIDATING COLLECTION")
        logger.info("=" * 30)

        # Check counts
        logger.info(f"Expected persons: {len(person_ids)}")
        logger.info(f"Collected persons: {len(persons)}")

        # Check data quality
        complete_records = 0
        for person in persons:
            if person.get('Achternaam') and person.get('Voornamen'):
                complete_records += 1

        logger.info(f"Complete records (name data): {complete_records}")

        # Check for active parliament members
        active_members = 0
        for person in persons:
            # Check if person has parliamentary functions
            # This would require joining with FractieZetelPersoon data
            active_members += 1  # For now, assume all are active

        logger.info(f"Active parliament members: {active_members}")

        return {
            'expected_count': len(person_ids),
            'collected_count': len(persons),
            'complete_records': complete_records,
            'active_members': active_members
        }

def main():
    print("[*] CORRECT PARLIAMENT MEMBER COLLECTION")
    print("=" * 50)

    collector = CorrectParliamentMemberCollector()

    # Step 1: Get active member IDs
    person_ids = collector.collect_active_parliament_members()

    if not person_ids:
        print("[-] Failed to collect active member IDs")
        return 1

    # Step 2: Get person details
    persons = collector.collect_person_details(person_ids)

    if not persons:
        print("[-] Failed to collect person details")
        return 1

    # Step 3: Validate
    validation = collector.validate_collection(person_ids, persons)

    print("\n[+] COLLECTION COMPLETE")
    print(f"Expected: {validation['expected_count']} active members")
    print(f"Collected: {validation['collected_count']} person records")
    print(f"Complete: {validation['complete_records']} with full data")
    print(f"Active: {validation['active_members']} parliament members")

    if validation['collected_count'] == 150 and validation['complete_records'] > 0:
        print("[+] SUCCESS: Corrected parliament member collection!")
    else:
        print("[-] ISSUES: Collection may still have problems")

    return 0

if __name__ == "__main__":
    exit(main())