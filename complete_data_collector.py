#!/usr/bin/env python3
"""
Complete Data Collector - Alle entity types voor afgelopen 30 dagen
Uitbreiding van eerdere collector om ALLE beschikbare data op te halen
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

class CompleteDataCollector:
    def __init__(self, base_dir="bronmateriaal-onbewerkt"):
        self.base_url = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"
        self.base_dir = Path(base_dir)
        
        # Alle bekende entity types
        self.entities = [
            'Zaak',           # Alle parlementaire zaken (moties, wetten, amendementen)
            'Stemming',       # Stemmingen (al verzameld, maar nu compleet)
            'Besluit',        # Besluiten
            'Document',       # Documenten en teksten
            'Activiteit',     # Parlementaire activiteiten
            'Persoon',        # Parlementariërs
            'Fractie',        # Partijen/fracties
            'Vergadering',    # Vergaderingen
            'Agendapunt',     # Agenda items
        ]
        
        # Zorg voor directories
        for entity in self.entities:
            (self.base_dir / entity.lower()).mkdir(parents=True, exist_ok=True)
    
    def clean_for_json(self, obj):
        """Maak object JSON-serializable door circulaire referenties te verwijderen"""
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
        
        # Clean data voor JSON serialization
        clean_data = self.clean_for_json(data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(clean_data, f, indent=2, ensure_ascii=False)
        
        file_size = filepath.stat().st_size
        logger.info(f"💾 Saved: {filepath.name} ({file_size/1024:.1f} KB)")
        
        return filepath
    
    def collect_entity_paginated(self, entity_name, days_back=30):
        """Verzamel alle data voor een entity type met paginatie"""
        logger.info(f"\n🔄 COLLECTING {entity_name.upper()} (last {days_back} days)")
        logger.info("=" * 60)
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        all_records = []
        skip = 0
        page = 1
        
        while True:
            logger.info(f"📄 Page {page} (skip {skip})...")
            
            try:
                # API call met paginatie
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
                    
                    # Filter by date (client-side voor betrouwbaarheid)
                    recent_records = []
                    for record in records:
                        record_date_str = record.get('GewijzigdOp', '')
                        if record_date_str:
                            try:
                                record_date = datetime.fromisoformat(record_date_str.replace('Z', '+00:00'))
                                if record_date.replace(tzinfo=None) >= cutoff_date:
                                    recent_records.append(record)
                                else:
                                    logger.info(f"  🛑 Reached records older than {days_back} days")
                                    all_records.extend(recent_records)
                                    # Save this page and return
                                    if recent_records:
                                        self.save_raw_response(entity_name.lower(), f'{entity_name.lower()}_page_{page}', recent_records, f'{days_back}days')
                                    return all_records
                            except:
                                # Als datum parsing faalt, neem record mee
                                recent_records.append(record)
                    
                    all_records.extend(recent_records)
                    
                    # Save page
                    if recent_records:
                        self.save_raw_response(entity_name.lower(), f'{entity_name.lower()}_page_{page}', recent_records, f'{days_back}days')
                    
                    # Check of we alle data hebben (minder dan 250 = einde)
                    if len(records) < 250:
                        logger.info(f"  ✅ Got {len(records)} records (less than 250), end of data")
                        break
                    
                    skip += 250
                    page += 1
                    time.sleep(0.5)  # Wees aardig voor de API
                    
                else:
                    logger.error(f"  ❌ Error fetching {entity_name} page {page}: {response.status_code}")
                    break
                    
            except Exception as e:
                logger.error(f"  ❌ Exception on {entity_name} page {page}: {e}")
                break
        
        logger.info(f"✅ Collected {len(all_records)} {entity_name} records from last {days_back} days")
        return all_records
    
    def collect_all_zaak_types(self, days_back=30):
        """Verzamel ALLE Zaak types (niet alleen moties)"""
        logger.info(f"\n🏛️ COLLECTING ALL ZAAK TYPES (last {days_back} days)")
        logger.info("=" * 55)
        
        # Gebruik de bestaande collector maar zonder Soort filter
        all_zaken = self.collect_entity_paginated('Zaak', days_back)
        
        # Analyseer de verzamelde types
        if all_zaken:
            soorten = {}
            for zaak in all_zaken:
                soort = zaak.get('Soort', 'Onbekend')
                if soort not in soorten:
                    soorten[soort] = 0
                soorten[soort] += 1
            
            logger.info(f"\n📊 ZAAK TYPES FOUND:")
            for soort, count in sorted(soorten.items()):
                logger.info(f"  {soort:30}: {count:4d} items")
        
        return all_zaken
    
    def collect_complete_30day_dataset(self):
        """Verzamel complete dataset voor alle entity types"""
        logger.info(f"🚀 STARTING COMPLETE 30-DAY DATA COLLECTION")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        results = {}
        
        for entity in self.entities:
            try:
                if entity == 'Zaak':
                    # Speciale behandeling voor Zaak (alle types)
                    records = self.collect_all_zaak_types(30)
                else:
                    # Normale collection voor andere entities
                    records = self.collect_entity_paginated(entity, 30)
                
                results[entity] = len(records)
                logger.info(f"✅ {entity}: {len(records)} records collected")
                
            except Exception as e:
                logger.error(f"❌ Failed to collect {entity}: {e}")
                results[entity] = 0
        
        # Samenvatting
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        logger.info(f"\n🎯 COLLECTION SUMMARY")
        logger.info("=" * 30)
        logger.info(f"⏱️ Duration: {duration:.1f} seconds")
        
        total_records = sum(results.values())
        logger.info(f"📊 Total records: {total_records}")
        
        for entity, count in results.items():
            logger.info(f"  {entity:12}: {count:5d} records")
        
        # Bereken totale data grootte
        total_size = 0
        for entity_dir in self.base_dir.iterdir():
            if entity_dir.is_dir():
                size = sum(f.stat().st_size for f in entity_dir.glob('*.json'))
                total_size += size
                if size > 0:
                    logger.info(f"  {entity_dir.name:12}: {size/1024/1024:.1f} MB")
        
        logger.info(f"\n💾 Total dataset size: {total_size/1024/1024:.1f} MB")
        logger.info(f"✅ Complete 30-day collection finished!")
        
        return results

if __name__ == "__main__":
    collector = CompleteDataCollector()
    results = collector.collect_complete_30day_dataset()
    
    print(f"\n🎉 SUCCESS!")
    print(f"Collected data for {len(results)} entity types")
    print(f"Ready for next phase: Full parliament term (Dec 2023 - now)")