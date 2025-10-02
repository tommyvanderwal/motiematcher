#!/usr/bin/env python3
"""
Full Parliament Term Data Collector
Verzamel ALLE parlamentaire data vanaf 6 december 2023 (huidige kamer samenstelling)
"""

import requests
import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FullTermCollector:
    def __init__(self, base_dir="bronmateriaal-onbewerkt"):
        self.base_url = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"
        self.base_dir = Path(base_dir)
        
        # Start datum huidige kamer samenstelling
        self.parliament_start = datetime(2023, 12, 6)  # 6 december 2023
        
        # Alle entity types
        self.entities = [
            'Zaak',           # Alle parlementaire zaken
            'Stemming',       # Stemmingen
            'Besluit',        # Besluiten
            'Document',       # Documenten
            'Activiteit',     # Activiteiten
            'Persoon',        # Parlementariërs
            'Fractie',        # Partijen
            'Vergadering',    # Vergaderingen
            'Agendapunt',     # Agenda items
        ]
        
        # Directories bestaan al van 30-day collection
    
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
    
    def collect_entity_full_term(self, entity_name):
        """Verzamel alle data voor een entity vanaf december 2023"""
        logger.info(f"\n🏛️ COLLECTING {entity_name.upper()} (Dec 6, 2023 - now)")
        logger.info("=" * 70)
        
        cutoff_date = self.parliament_start
        days_total = (datetime.now() - cutoff_date).days
        
        logger.info(f"📅 Period: {days_total} days ({cutoff_date.strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')})")
        
        all_records = []
        skip = 0
        page = 1
        
        while True:
            logger.info(f"📄 Page {page} (skip {skip})...")
            
            try:
                url = f"{self.base_url}/{entity_name}?$skip={skip}&$orderby=GewijzigdOp desc"
                response = requests.get(url)
                
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
                                if record_date.replace(tzinfo=None) >= cutoff_date:
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
                            entity_name.lower(), 
                            f'{entity_name.lower()}_page_{page}', 
                            recent_records, 
                            'fullterm'
                        )
                    
                    # Als we veel oude records tegenkomen, zijn we klaar
                    if old_count > len(recent_records) * 2:  # Meer oude dan nieuwe
                        logger.info(f"  ✅ Reached historical data threshold")
                        break
                    
                    # Check of we alle data hebben (minder dan 250 = einde API)
                    if len(records) < 250:
                        logger.info(f"  ✅ Got {len(records)} records (less than 250), end of API data")
                        break
                    
                    skip += 250
                    page += 1
                    time.sleep(0.5)  # API vriendelijk
                    
                    # Progress feedback elke 10 pagina's
                    if page % 10 == 0:
                        logger.info(f"  📊 Progress: {len(all_records)} records collected so far...")
                    
                else:
                    logger.error(f"  ❌ Error fetching {entity_name} page {page}: {response.status_code}")
                    break
                    
            except Exception as e:
                logger.error(f"  ❌ Exception on {entity_name} page {page}: {e}")
                break
        
        logger.info(f"✅ {entity_name}: {len(all_records)} records collected from full parliamentary term")
        return all_records
    
    def collect_full_parliament_term(self):
        """Verzamel complete dataset voor volledige parlementaire termijn"""
        logger.info(f"🏛️ STARTING FULL PARLIAMENT TERM COLLECTION")
        logger.info(f"📅 Period: December 6, 2023 - {datetime.now().strftime('%B %d, %Y')}")
        logger.info("=" * 80)
        
        start_time = datetime.now()
        results = {}
        
        for entity in self.entities:
            try:
                logger.info(f"\n⏰ Starting {entity} collection at {datetime.now().strftime('%H:%M:%S')}")
                records = self.collect_entity_full_term(entity)
                results[entity] = len(records)
                
                logger.info(f"✅ {entity}: {len(records)} records collected")
                
                # Korte pauze tussen entities
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Failed to collect {entity}: {e}")
                results[entity] = 0
        
        # Final summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"\n🎯 FULL TERM COLLECTION SUMMARY")
        logger.info("=" * 50)
        logger.info(f"⏱️ Total duration: {duration/60:.1f} minutes")
        
        total_records = sum(results.values())
        logger.info(f"📊 Total records: {total_records:,}")
        
        for entity, count in results.items():
            logger.info(f"  {entity:12}: {count:6,} records")
        
        # Calculate total dataset size
        total_size = 0
        for entity_dir in self.base_dir.iterdir():
            if entity_dir.is_dir():
                size = sum(f.stat().st_size for f in entity_dir.glob('*fullterm*.json'))
                total_size += size
                if size > 0:
                    logger.info(f"  {entity_dir.name:12}: {size/1024/1024:.1f} MB (new)")
        
        logger.info(f"\n💾 Full term dataset size: {total_size/1024/1024:.1f} MB")
        logger.info(f"🎉 COMPLETE PARLIAMENT TERM COLLECTION FINISHED!")
        
        return results

if __name__ == "__main__":
    collector = FullTermCollector()
    
    print("🏛️ DUTCH PARLIAMENT FULL TERM DATA COLLECTION")
    print("=" * 60)
    print("📅 Collecting all parliamentary data since December 6, 2023")
    print("🎯 Target: Complete dataset for current parliament composition")
    print("⏱️ Estimated time: 15-30 minutes")
    print("💾 Estimated size: ~500 MB")
    print()
    
    confirm = input("🚀 Start full collection? (y/n): ")
    if confirm.lower() == 'y':
        results = collector.collect_full_parliament_term()
        
        print(f"\n🎉 SUCCESS!")
        print(f"Complete parliamentary dataset collected!")
        print(f"Ready for data transformation and web platform development!")
    else:
        print("Collection cancelled.")