"""
Extended ETL Data Collector for 30 days with pagination and complete motie texts
Includes modular refresh system and proper motie text collection via Zaak entities
"""

import requests
import json
from datetime import datetime, timedelta
import logging
import time
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExtendedDataCollector:
    """Extended data collector with 30-day support, pagination, and motie text collection"""
    
    def __init__(self):
        self.base_url = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MotieMatcher-ExtendedETL/1.0',
            'Accept': 'application/json'
        })
        
        # Set up directory structure
        self.raw_data_dir = Path("bronmateriaal-onbewerkt")
        self.raw_data_dir.mkdir(exist_ok=True)
        
        # Subdirectories for different data types
        self.subdirs = {
            'besluit': self.raw_data_dir / 'besluit',
            'stemming': self.raw_data_dir / 'stemming', 
            'agendapunt': self.raw_data_dir / 'agendapunt',
            'document': self.raw_data_dir / 'document',
            'zaak': self.raw_data_dir / 'zaak',
            'activiteit': self.raw_data_dir / 'activiteit'
        }
        
        for subdir in self.subdirs.values():
            subdir.mkdir(exist_ok=True)
    
    def save_raw_response(self, data_type, endpoint, data, additional_info=""):
        """Save raw API response to appropriate directory with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if additional_info:
            filename = f"{endpoint}_{additional_info}_{timestamp}.json"
        else:
            filename = f"{endpoint}_{timestamp}.json"
        
        filepath = self.subdirs[data_type] / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📁 Saved raw data: {filepath}")
        return filepath
    
    def paginated_request(self, entity_type, filters=None, expand=None, days_back=30, max_records=None):
        """Make paginated requests to handle API limits (250 per request)"""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        logger.info(f"🔄 Starting paginated collection of {entity_type} (last {days_back} days)")
        
        url = f"{self.base_url}/{entity_type}"
        
        base_params = {
            '$orderby': 'GewijzigdOp desc',
            '$top': 250  # API maximum
        }
        
        if filters:
            base_params['$filter'] = filters
        
        if expand:
            base_params['$expand'] = expand
        
        all_records = []
        skip = 0
        page = 1
        
        while True:
            params = base_params.copy()
            if skip > 0:
                params['$skip'] = skip
            
            try:
                logger.info(f"  📄 Page {page}: fetching records {skip+1}-{skip+250}")
                response = self.session.get(url, params=params, timeout=60)
                
                if response.status_code == 200:
                    data = response.json()
                    records = data.get('value', [])
                    
                    if not records:
                        logger.info(f"  ✅ No more records found, stopping pagination")
                        break
                    
                    # Filter by date in code (more reliable)
                    filtered_records = []
                    for record in records:
                        record_date_str = record.get('GewijzigdOp', '')
                        if record_date_str:
                            try:
                                record_date = datetime.fromisoformat(record_date_str.replace('Z', '+00:00'))
                                if record_date.replace(tzinfo=None) >= cutoff_date:
                                    filtered_records.append(record)
                                else:
                                    # If we're past the cutoff date, we can stop
                                    logger.info(f"  🛑 Reached records older than {days_back} days, stopping")
                                    all_records.extend(filtered_records)
                                    # Save this page
                                    page_info = f"page_{page}_{days_back}days"
                                    self.save_raw_response(entity_type.lower(), f"paginated_{entity_type.lower()}", {
                                        'page': page,
                                        'skip': skip,
                                        'records': filtered_records,
                                        'cutoff_reached': True
                                    }, page_info)
                                    return all_records
                            except:
                                pass  # Skip invalid dates\n                    \n                    all_records.extend(filtered_records)\n                    \n                    # Save page data\n                    page_info = f\"page_{page}_{days_back}days\"\n                    self.save_raw_response(entity_type.lower(), f\"paginated_{entity_type.lower()}\", {\n                        'page': page,\n                        'skip': skip,\n                        'records': filtered_records,\n                        'total_in_page': len(records),\n                        'filtered_in_page': len(filtered_records)\n                    }, page_info)\n                    \n                    # Check if we got less than 250 records (end of data)\n                    if len(records) < 250:\n                        logger.info(f\"  ✅ Got {len(records)} records (less than 250), end of data\")\n                        break\n                    \n                    # Check max records limit\n                    if max_records and len(all_records) >= max_records:\n                        logger.info(f\"  🎯 Reached max_records limit of {max_records}\")\n                        break\n                    \n                    skip += 250\n                    page += 1\n                    \n                    # Be nice to the API\n                    time.sleep(0.5)\n                    \n                else:\n                    logger.error(f\"  ❌ Error on page {page}: {response.status_code}\")\n                    logger.error(f\"  Response: {response.text[:300]}\")\n                    break\n                    \n            except Exception as e:\n                logger.error(f\"  ❌ Exception on page {page}: {e}\")\n                break\n        \n        logger.info(f\"🎉 Collected {len(all_records)} {entity_type} records from last {days_back} days\")\n        \n        # Save complete collection summary\n        summary = {\n            'entity_type': entity_type,\n            'days_back': days_back,\n            'total_records': len(all_records),\n            'pages_fetched': page,\n            'collection_date': datetime.now().isoformat(),\n            'cutoff_date': cutoff_date.isoformat()\n        }\n        \n        self.save_raw_response(entity_type.lower(), f\"complete_{entity_type.lower()}\", {\n            'summary': summary,\n            'all_records': all_records\n        }, f\"{days_back}days_complete\")\n        \n        return all_records\n    \n    def get_motie_texts_from_zaak(self, days_back=30):\n        \"\"\"Get all Zaak entities with Soort='Motie' to get actual motion texts\"\"\"\n        logger.info(f\"🎯 Collecting motie texts via Zaak entities (last {days_back} days)\")\n        \n        # Get Zaak entities that are moties\n        moties = self.paginated_request(\n            entity_type=\"Zaak\",\n            filters=\"Verwijderd eq false and Soort eq 'Motie'\",\n            expand=\"ZaakActor,Document\",\n            days_back=days_back\n        )\n        \n        logger.info(f\"✅ Found {len(moties)} moties from Zaak entities\")\n        \n        # Process each motie for detailed text information\n        motie_details = []\n        for i, motie in enumerate(moties):\n            detail = {\n                'zaak_id': motie.get('Id'),\n                'nummer': motie.get('Nummer'),\n                'titel': motie.get('Titel', ''),\n                'onderwerp': motie.get('Onderwerp', ''),\n                'status': motie.get('Status', ''),\n                'vergaderjaar': motie.get('Vergaderjaar', ''),\n                'gestartop': motie.get('GestartOp', ''),\n                'organisatie': motie.get('Organisatie', ''),\n                'huidige_behandelstatus': motie.get('HuidigeBehandelstatus', ''),\n                'kabinetsappreciatie': motie.get('Kabinetsappreciatie', ''),\n                'afgedaan': motie.get('Afgedaan', False),\n                'groot_project': motie.get('GrootProject', False),\n                'zaak_actors': motie.get('ZaakActor', []),\n                'documents': motie.get('Document', []),\n                'modified_date': motie.get('GewijzigdOp', '')\n            }\n            \n            motie_details.append(detail)\n        \n        # Save motie texts summary\n        self.save_raw_response('zaak', 'motie_texts', {\n            'collection_date': datetime.now().isoformat(),\n            'days_back': days_back,\n            'total_moties': len(motie_details),\n            'motie_details': motie_details\n        }, f\"last_{days_back}_days\")\n        \n        return motie_details\n    \n    def get_extended_voting_data(self, days_back=30):\n        \"\"\"Get comprehensive voting data for 30 days with pagination\"\"\"\n        logger.info(f\"🗳️ Collecting extended voting data (last {days_back} days)\")\n        \n        # Get all voting records\n        votes = self.paginated_request(\n            entity_type=\"Stemming\",\n            filters=\"Verwijderd eq false\",\n            expand=\"Besluit,Fractie,Persoon\",\n            days_back=days_back\n        )\n        \n        # Group votes by decision\n        decisions_votes = {}\n        for vote in votes:\n            decision_id = vote.get('Besluit_Id')\n            if decision_id:\n                if decision_id not in decisions_votes:\n                    decisions_votes[decision_id] = []\n                decisions_votes[decision_id].append(vote)\n        \n        logger.info(f\"✅ Found {len(votes)} votes for {len(decisions_votes)} decisions\")\n        \n        return votes, decisions_votes\n    \n    def collect_30_day_comprehensive_data(self):\n        \"\"\"Main method to collect comprehensive 30-day parliamentary data\"\"\"\n        logger.info(f\"🚀 Starting comprehensive 30-day data collection\")\n        \n        start_time = datetime.now()\n        \n        # 1. Get motie texts via Zaak entities\n        logger.info(f\"\\n📝 STEP 1: Collecting motie texts\")\n        moties = self.get_motie_texts_from_zaak(30)\n        \n        # 2. Get voting data\n        logger.info(f\"\\n🗳️ STEP 2: Collecting voting data\")\n        votes, decisions_votes = self.get_extended_voting_data(30)\n        \n        # 3. Get recent decisions that have voting\n        logger.info(f\"\\n⚖️ STEP 3: Collecting besluit data\")\n        besluiten = self.paginated_request(\n            entity_type=\"Besluit\",\n            filters=\"Verwijderd eq false\",\n            expand=\"Agendapunt,Zaak,Stemming\",\n            days_back=30\n        )\n        \n        # Filter to only decisions with voting\n        besluiten_with_voting = [b for b in besluiten if b.get('Id') in decisions_votes]\n        \n        # 4. Get agendapunt data\n        logger.info(f\"\\n📋 STEP 4: Collecting agendapunt data\")\n        agendapunten = self.paginated_request(\n            entity_type=\"Agendapunt\",\n            filters=\"Verwijderd eq false\",\n            expand=\"Activiteit,Besluit,Document,Zaak\",\n            days_back=30,\n            max_records=1000  # Limit to avoid too much data\n        )\n        \n        # 5. Compile comprehensive summary\n        end_time = datetime.now()\n        duration = (end_time - start_time).total_seconds()\n        \n        comprehensive_summary = {\n            'collection_metadata': {\n                'start_time': start_time.isoformat(),\n                'end_time': end_time.isoformat(),\n                'duration_seconds': duration,\n                'days_collected': 30,\n                'api_base_url': self.base_url\n            },\n            'data_summary': {\n                'moties_found': len(moties),\n                'votes_found': len(votes),\n                'decisions_with_voting': len(besluiten_with_voting),\n                'total_besluiten': len(besluiten),\n                'agendapunten_collected': len(agendapunten)\n            },\n            'sample_moties': moties[:5],  # First 5 for preview\n            'sample_decisions_with_voting': [\n                {\n                    'id': b.get('Id'),\n                    'text': b.get('BesluitTekst', ''),\n                    'type': b.get('BesluitSoort', ''),\n                    'voting_type': b.get('StemmingsSoort', ''),\n                    'vote_count': len(decisions_votes.get(b.get('Id'), [])),\n                    'date': b.get('GewijzigdOp', '')\n                }\n                for b in besluiten_with_voting[:5]\n            ]\n        }\n        \n        # Save comprehensive summary\n        summary_file = self.raw_data_dir / f\"comprehensive_30day_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json\"\n        with open(summary_file, 'w', encoding='utf-8') as f:\n            json.dump(comprehensive_summary, f, indent=2, ensure_ascii=False)\n        \n        logger.info(f\"\\n🎉 30-DAY COLLECTION COMPLETE!\")\n        logger.info(f\"   ⏱️ Duration: {duration:.1f} seconds\")\n        logger.info(f\"   📊 Summary saved: {summary_file}\")\n        \n        return comprehensive_summary\n\ndef main():\n    \"\"\"Main execution for 30-day data collection\"\"\"\n    collector = ExtendedDataCollector()\n    \n    # Collect comprehensive 30-day data\n    summary = collector.collect_30_day_comprehensive_data()\n    \n    print(f\"\\n🎯 30-DAY COMPREHENSIVE DATA COLLECTION RESULTS:\")\n    print(f\"📁 Raw data stored in: {collector.raw_data_dir}\")\n    print(f\"\\n📊 COLLECTION SUMMARY:\")\n    print(f\"   🏛️ Moties found: {summary['data_summary']['moties_found']}\")\n    print(f\"   🗳️ Votes collected: {summary['data_summary']['votes_found']}\")\n    print(f\"   ⚖️ Decisions with voting: {summary['data_summary']['decisions_with_voting']}\")\n    print(f\"   📋 Agendapunten: {summary['data_summary']['agendapunten_collected']}\")\n    print(f\"   ⏱️ Collection time: {summary['collection_metadata']['duration_seconds']:.1f} seconds\")\n    \n    if summary['sample_moties']:\n        print(f\"\\n📝 SAMPLE MOTIES:\")\n        for i, motie in enumerate(summary['sample_moties']):\n            print(f\"   {i+1}. {motie['titel'][:80]}...\")\n            print(f\"      Status: {motie['status']} | Jaar: {motie['vergaderjaar']}\")\n            print(f\"      Onderwerp: {motie['onderwerp'][:60]}...\")\n            print()\n    \n    if summary['sample_decisions_with_voting']:\n        print(f\"📊 SAMPLE VOTING DECISIONS:\")\n        for i, decision in enumerate(summary['sample_decisions_with_voting']):\n            print(f\"   {i+1}. {decision['text'][:60]}...\")\n            print(f\"      Type: {decision['type']} | Votes: {decision['vote_count']}\")\n    \n    return summary\n\nif __name__ == \"__main__\":\n    main()