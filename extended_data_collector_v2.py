"""
Extended ETL Data Collector for 30 days with pagination and complete motie texts
"""

import requests
import json
from datetime import datetime, timedelta
import logging
import time
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
    
    def get_motie_texts_from_zaak(self, days_back=30):
        """Get all Zaak entities with Soort='Motie' to get actual motion texts"""
        logger.info(f"🎯 Collecting motie texts via Zaak entities (last {days_back} days)")
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        url = f"{self.base_url}/Zaak"
        params = {
            '$filter': "Verwijderd eq false and Soort eq 'Motie'",
            '$orderby': 'GewijzigdOp desc',
            '$top': 250,
            '$expand': 'ZaakActor,Document'
        }
        
        all_moties = []
        skip = 0
        page = 1
        
        while True:
            if skip > 0:
                params['$skip'] = skip
            
            try:
                logger.info(f"  📄 Page {page}: fetching moties {skip+1}-{skip+250}")
                response = self.session.get(url, params=params, timeout=60)
                
                if response.status_code == 200:
                    data = response.json()
                    moties = data.get('value', [])
                    
                    if not moties:
                        logger.info(f"  ✅ No more moties found")
                        break
                    
                    # Filter by date
                    recent_moties = []
                    for motie in moties:
                        motie_date_str = motie.get('GewijzigdOp', '')
                        if motie_date_str:
                            try:
                                motie_date = datetime.fromisoformat(motie_date_str.replace('Z', '+00:00'))
                                if motie_date.replace(tzinfo=None) >= cutoff_date:
                                    recent_moties.append(motie)
                                else:
                                    logger.info(f"  🛑 Reached moties older than {days_back} days")
                                    all_moties.extend(recent_moties)
                                    self.save_raw_response('zaak', f'moties_page_{page}', recent_moties, f'{days_back}days')
                                    return all_moties
                            except:
                                pass
                    
                    all_moties.extend(recent_moties)
                    self.save_raw_response('zaak', f'moties_page_{page}', recent_moties, f'{days_back}days')
                    
                    if len(moties) < 250:
                        logger.info(f"  ✅ Got {len(moties)} moties (less than 250), end of data")
                        break
                    
                    skip += 250
                    page += 1
                    time.sleep(0.5)
                    
                else:
                    logger.error(f"  ❌ Error fetching moties page {page}: {response.status_code}")
                    break
                    
            except Exception as e:
                logger.error(f"  ❌ Exception on page {page}: {e}")
                break
        
        logger.info(f"✅ Found {len(all_moties)} moties from last {days_back} days")
        
        # Process motie details
        motie_details = []
        for motie in all_moties:
            detail = {
                'zaak_id': motie.get('Id'),
                'nummer': motie.get('Nummer'),
                'titel': motie.get('Titel', ''),
                'onderwerp': motie.get('Onderwerp', ''),
                'status': motie.get('Status', ''),
                'vergaderjaar': motie.get('Vergaderjaar', ''),
                'gestartop': motie.get('GestartOp', ''),
                'organisatie': motie.get('Organisatie', ''),
                'huidige_behandelstatus': motie.get('HuidigeBehandelstatus', ''),
                'kabinetsappreciatie': motie.get('Kabinetsappreciatie', ''),
                'afgedaan': motie.get('Afgedaan', False),
                'groot_project': motie.get('GrootProject', False),
                'zaak_actors': motie.get('ZaakActor', []),
                'documents': motie.get('Document', []),
                'modified_date': motie.get('GewijzigdOp', '')
            }
            motie_details.append(detail)
        
        # Save complete motie collection
        self.save_raw_response('zaak', 'complete_moties', {
            'collection_date': datetime.now().isoformat(),
            'days_back': days_back,
            'total_moties': len(motie_details),
            'motie_details': motie_details
        }, f'last_{days_back}_days')
        
        return motie_details
    
    def get_extended_voting_data(self, days_back=30):
        """Get comprehensive voting data with pagination"""
        logger.info(f"🗳️ Collecting extended voting data (last {days_back} days)")
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        url = f"{self.base_url}/Stemming"
        params = {
            '$filter': 'Verwijderd eq false',
            '$orderby': 'GewijzigdOp desc',
            '$top': 250,
            '$expand': 'Besluit,Fractie,Persoon'
        }
        
        all_votes = []
        skip = 0
        page = 1
        
        while True:
            if skip > 0:
                params['$skip'] = skip
            
            try:
                logger.info(f"  📄 Page {page}: fetching votes {skip+1}-{skip+250}")
                response = self.session.get(url, params=params, timeout=60)
                
                if response.status_code == 200:
                    data = response.json()
                    votes = data.get('value', [])
                    
                    if not votes:
                        logger.info(f"  ✅ No more votes found")
                        break
                    
                    # Filter by date
                    recent_votes = []
                    for vote in votes:
                        vote_date_str = vote.get('GewijzigdOp', '')
                        if vote_date_str:
                            try:
                                vote_date = datetime.fromisoformat(vote_date_str.replace('Z', '+00:00'))
                                if vote_date.replace(tzinfo=None) >= cutoff_date:
                                    recent_votes.append(vote)
                                else:
                                    logger.info(f"  🛑 Reached votes older than {days_back} days")
                                    all_votes.extend(recent_votes)
                                    self.save_raw_response('stemming', f'votes_page_{page}', recent_votes, f'{days_back}days')
                                    # Group votes by decision before returning
                                    decisions_votes = {}
                                    for vote in all_votes:
                                        decision_id = vote.get('Besluit_Id')
                                        if decision_id:
                                            if decision_id not in decisions_votes:
                                                decisions_votes[decision_id] = []
                                            decisions_votes[decision_id].append(vote)
                                    return all_votes, decisions_votes
                            except:
                                pass
                    
                    all_votes.extend(recent_votes)
                    self.save_raw_response('stemming', f'votes_page_{page}', recent_votes, f'{days_back}days')
                    
                    if len(votes) < 250:
                        logger.info(f"  ✅ Got {len(votes)} votes (less than 250), end of data")
                        break
                    
                    skip += 250
                    page += 1
                    time.sleep(0.5)
                    
                else:
                    logger.error(f"  ❌ Error fetching votes page {page}: {response.status_code}")
                    break
                    
            except Exception as e:
                logger.error(f"  ❌ Exception on page {page}: {e}")
                break
        
        logger.info(f"✅ Found {len(all_votes)} votes from last {days_back} days")
        
        # Group votes by decision
        decisions_votes = {}
        for vote in all_votes:
            decision_id = vote.get('Besluit_Id')
            if decision_id:
                if decision_id not in decisions_votes:
                    decisions_votes[decision_id] = []
                decisions_votes[decision_id].append(vote)
        
        logger.info(f"📊 Votes grouped into {len(decisions_votes)} decisions")
        
        # Save complete voting collection  
        self.save_raw_response('stemming', 'complete_votes', {
            'collection_date': datetime.now().isoformat(),
            'days_back': days_back,
            'total_votes': len(all_votes),
            'decisions_with_votes': len(decisions_votes)
        }, f'last_{days_back}_days')
        
        return all_votes, decisions_votes
    
    def collect_30_day_comprehensive_data(self):
        """Main method to collect comprehensive 30-day parliamentary data"""
        logger.info(f"🚀 Starting comprehensive 30-day data collection")
        
        start_time = datetime.now()
        
        # 1. Get motie texts via Zaak entities
        logger.info(f"\\n📝 STEP 1: Collecting motie texts")
        moties = self.get_motie_texts_from_zaak(30)
        
        # 2. Get voting data
        logger.info(f"\\n🗳️ STEP 2: Collecting voting data")
        votes, decisions_votes = self.get_extended_voting_data(30)
        
        # 3. Compile comprehensive summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        comprehensive_summary = {
            'collection_metadata': {
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': duration,
                'days_collected': 30,
                'api_base_url': self.base_url
            },
            'data_summary': {
                'moties_found': len(moties),
                'votes_found': len(votes),
                'decisions_with_voting': len(decisions_votes)
            },
            'sample_moties': moties[:10] if len(moties) > 10 else moties,
            'sample_decisions_with_voting': [
                {
                    'decision_id': decision_id,
                    'vote_count': len(vote_list)
                }
                for decision_id, vote_list in list(decisions_votes.items())[:10]
            ]
        }
        
        # Save comprehensive summary
        summary_file = self.raw_data_dir / f"comprehensive_30day_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\\n🎉 30-DAY COLLECTION COMPLETE!")
        logger.info(f"   ⏱️ Duration: {duration:.1f} seconds")
        logger.info(f"   📊 Summary saved: {summary_file}")
        
        return comprehensive_summary

def main():
    """Main execution for 30-day data collection"""
    collector = ExtendedDataCollector()
    
    # Collect comprehensive 30-day data
    summary = collector.collect_30_day_comprehensive_data()
    
    print(f"\\n🎯 30-DAY COMPREHENSIVE DATA COLLECTION RESULTS:")
    print(f"📁 Raw data stored in: {collector.raw_data_dir}")
    print(f"\\n📊 COLLECTION SUMMARY:")
    print(f"   🏛️ Moties found: {summary['data_summary']['moties_found']}")
    print(f"   🗳️ Votes collected: {summary['data_summary']['votes_found']}")
    print(f"   ⚖️ Decisions with voting: {summary['data_summary']['decisions_with_voting']}")
    print(f"   ⏱️ Collection time: {summary['collection_metadata']['duration_seconds']:.1f} seconds")
    
    if summary['sample_moties']:
        print(f"\\n📝 SAMPLE MOTIES:")
        for i, motie in enumerate(summary['sample_moties'][:5]):
            print(f"   {i+1}. {motie.get('titel', 'Geen titel')[:80]}...")
            print(f"      Status: {motie.get('status', 'Onbekend')} | Jaar: {motie.get('vergaderjaar', 'Onbekend')}")
            if motie.get('onderwerp'):
                print(f"      Onderwerp: {motie['onderwerp'][:60]}...")
            print()
    
    return summary

if __name__ == "__main__":
    main()