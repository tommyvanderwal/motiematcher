"""
Complete ETL Data Collector for Dutch Parliamentary Data
Collects comprehensive motion data from last 10 days with full details and texts
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

class ComprehensiveDataCollector:
    """Comprehensive data collector for Dutch parliamentary motions with full details"""
    
    def __init__(self):
        self.base_url = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MotieMatcher-ComprehensiveETL/1.0',
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
            'zaak': self.raw_data_dir / 'zaak'
        }
        
        for subdir in self.subdirs.values():
            subdir.mkdir(exist_ok=True)
    
    def clean_for_json(self, obj, seen=None):
        """Remove circular references from object for JSON serialization"""
        if seen is None:
            seen = set()
        
        if isinstance(obj, dict):
            obj_id = id(obj)
            if obj_id in seen:
                return {"_circular_reference": True, "_type": "dict"}
            seen.add(obj_id)
            
            cleaned = {}
            for key, value in obj.items():
                cleaned[key] = self.clean_for_json(value, seen.copy())
            return cleaned
            
        elif isinstance(obj, list):
            return [self.clean_for_json(item, seen.copy()) for item in obj]
        else:
            return obj
    
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
    
    def get_recent_voting_records(self, days_back=10):
        """Get all voting records from last N days, then find their decisions"""
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        logger.info(f"🔍 Fetching recent voting records (targeting last {days_back} days since {cutoff_date.date()})")
        
        url = f"{self.base_url}/Stemming"
        
        params = {
            '$filter': 'Verwijderd eq false',
            '$orderby': 'GewijzigdOp desc',
            '$top': 250,  # API maximum
            '$expand': 'Besluit,Fractie,Persoon'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                all_votes = data.get('value', [])
                
                # Filter for recent votes in code (more reliable than API filter)
                recent_votes = []
                for vote in all_votes:
                    vote_date_str = vote.get('GewijzigdOp', '')
                    if vote_date_str:
                        try:
                            vote_date = datetime.fromisoformat(vote_date_str.replace('Z', '+00:00'))
                            if vote_date.replace(tzinfo=None) >= cutoff_date:
                                recent_votes.append(vote)
                        except:
                            pass  # Skip invalid dates
                
                # Save raw voting response
                self.save_raw_response('stemming', 'recent_votes', data, f"last_{days_back}_days")
                
                logger.info(f"✅ Found {len(all_votes)} total votes, {len(recent_votes)} from last {days_back} days")
                return recent_votes
            else:
                logger.error(f"❌ Error fetching votes: {response.status_code}")
                logger.error(f"Response: {response.text[:500]}")
                return []
                
        except Exception as e:
            logger.error(f"Exception fetching votes: {e}")
            return []
    
    def get_decisions_from_votes(self, votes):
        """Extract unique decisions from voting records"""
        decision_ids = set()
        decisions = {}
        
        for vote in votes:
            decision_id = vote.get('Besluit_Id')
            if decision_id and decision_id not in decision_ids:
                decision_ids.add(decision_id)
                besluit = vote.get('Besluit')
                if besluit:
                    decisions[decision_id] = besluit
                    decisions[decision_id]['_votes'] = []
        
        # Add votes to their decisions
        for vote in votes:
            decision_id = vote.get('Besluit_Id')
            if decision_id in decisions:
                decisions[decision_id]['_votes'].append(vote)
        
        decision_list = list(decisions.values())
        logger.info(f"✅ Extracted {len(decision_list)} unique decisions with voting")
        
        return decision_list
    
    def get_agendapunt_details(self, agendapunt_id):
        """Get full details for an agenda item"""
        url = f"{self.base_url}/Agendapunt(guid'{agendapunt_id}')"
        
        params = {
            '$expand': 'Activiteit,Document,Zaak'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                self.save_raw_response('agendapunt', 'details', data, agendapunt_id[:8])
                return data
            else:
                logger.debug(f"Could not fetch agendapunt {agendapunt_id}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.debug(f"Error fetching agendapunt {agendapunt_id}: {e}")
            return None
    
    def get_document_details_with_content(self, document_id):
        """Get document details including actual content/text"""
        url = f"{self.base_url}/Document(guid'{document_id}')"
        
        params = {
            '$expand': 'DocumentVersie,HuidigeDocumentVersie,DocumentActor,Zaak'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                self.save_raw_response('document', 'details', data, document_id[:8])
                
                # Try to get document content/text
                document_versions = data.get('DocumentVersie', [])
                for version in document_versions:
                    version_id = version.get('Id')
                    if version_id:
                        content = self.get_document_version_content(version_id)
                        if content:
                            version['_content'] = content
                
                return data
            else:
                logger.debug(f"Could not fetch document {document_id}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.debug(f"Error fetching document {document_id}: {e}")
            return None
    
    def get_document_version_content(self, version_id):
        """Try to get actual document content/text"""
        url = f"{self.base_url}/DocumentVersie(guid'{version_id}')"
        
        params = {
            '$expand': 'DocumentPublicatie,DocumentPublicatieMetadata'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for document publication URLs
                publications = data.get('DocumentPublicatie', [])
                for pub in publications:
                    if pub.get('Url'):
                        logger.info(f"📄 Found document URL: {pub.get('Url')}")
                
                return data
            else:
                return None
                
        except Exception as e:
            logger.debug(f"Error fetching document version {version_id}: {e}")
            return None
    
    def get_zaak_details(self, zaak_id):
        """Get full case/zaak details"""
        url = f"{self.base_url}/Zaak(guid'{zaak_id}')"
        
        params = {
            '$expand': 'ZaakActor,Document,Activiteit'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                self.save_raw_response('zaak', 'details', data, zaak_id[:8])
                return data
            else:
                logger.debug(f"Could not fetch zaak {zaak_id}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.debug(f"Error fetching zaak {zaak_id}: {e}")
            return None
    
    def collect_comprehensive_motion_data(self, days_back=10):
        """Main method to collect all comprehensive motion data"""
        logger.info(f"🚀 Starting comprehensive data collection for last {days_back} days")
        
        # 1. Get all recent voting records 
        votes = self.get_recent_voting_records(days_back)
        
        if not votes:
            logger.error("No voting records found!")
            return []
        
        # 2. Extract decisions from votes
        decisions = self.get_decisions_from_votes(votes)
        
        if not decisions:
            logger.error("No decisions found!")
            return []
        
        comprehensive_motions = []
        
        for i, decision in enumerate(decisions):
            logger.info(f"📊 Processing decision {i+1}/{len(decisions)}: {decision.get('Id', 'Unknown')[:8]}...")
            
            motion_data = {
                'decision': decision,
                'votes': decision.get('_votes', []),  # Include the votes
                'agendapunt': None,
                'documents': [],
                'zaak': None,
                'enriched_content': {}
            }
            
            # 2. Get agendapunt details if available
            agendapunt_id = decision.get('Agendapunt_Id')
            if agendapunt_id:
                agendapunt = self.get_agendapunt_details(agendapunt_id)
                if agendapunt:
                    motion_data['agendapunt'] = agendapunt
                    
                    # Get documents linked to agendapunt
                    documents = agendapunt.get('Document', [])
                    for doc in documents:
                        doc_id = doc.get('Id')
                        if doc_id:
                            doc_details = self.get_document_details_with_content(doc_id)
                            if doc_details:
                                motion_data['documents'].append(doc_details)
            
            # 3. Get zaak details if available  
            zaak_list = decision.get('Zaak', [])
            if zaak_list:
                for zaak in zaak_list:
                    zaak_id = zaak.get('Id')
                    if zaak_id:
                        zaak_details = self.get_zaak_details(zaak_id)
                        if zaak_details:
                            motion_data['zaak'] = zaak_details
                            break  # Take first one
            
            # 4. Extract key information for easy access
            motion_data['enriched_content'] = {
                'title': decision.get('BesluitTekst', 'Geen titel'),
                'decision_type': decision.get('BesluitSoort', 'Onbekend'),
                'voting_type': decision.get('StemmingsSoort', 'Onbekend'),
                'status': decision.get('Status', 'Onbekend'),
                'date': decision.get('GewijzigdOp', ''),
                'agenda_subject': motion_data['agendapunt'].get('Onderwerp', '') if motion_data['agendapunt'] else '',
                'case_title': motion_data['zaak'].get('Titel', '') if motion_data['zaak'] else '',
                'document_count': len(motion_data['documents']),
                'voting_count': len(motion_data['votes'])
            }
            
            comprehensive_motions.append(motion_data)
            
            # Save individual motion data (clean for JSON serialization)
            motion_id = decision.get('Id', f'motion_{i}')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            motion_file = self.raw_data_dir / f"comprehensive_motion_{motion_id[:8]}_{timestamp}.json"
            
            # Clean circular references for JSON serialization
            clean_motion_data = self.clean_for_json(motion_data)
            
            with open(motion_file, 'w', encoding='utf-8') as f:
                json.dump(clean_motion_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 Saved comprehensive motion: {motion_file}")
            
            # Be nice to the API
            time.sleep(0.2)
        
        # Save summary
        summary = {
            'collection_date': datetime.now().isoformat(),
            'days_back': days_back,
            'total_motions': len(comprehensive_motions),
            'motions_summary': [
                {
                    'id': m['decision'].get('Id'),
                    'title': m['enriched_content']['title'],
                    'date': m['enriched_content']['date'],
                    'voting_count': m['enriched_content']['voting_count'],
                    'document_count': m['enriched_content']['document_count']
                }
                for m in comprehensive_motions
            ]
        }
        
        summary_file = self.raw_data_dir / f"collection_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📋 Collection summary saved: {summary_file}")
        logger.info(f"🎉 Comprehensive data collection complete! {len(comprehensive_motions)} motions collected")
        
        return comprehensive_motions

def main():
    """Main execution"""
    collector = ComprehensiveDataCollector()
    
    # Collect comprehensive data for last 10 days
    motions = collector.collect_comprehensive_motion_data(days_back=10)
    
    print(f"\n🎯 COMPREHENSIVE DATA COLLECTION RESULTS:")
    print(f"📊 Total motions collected: {len(motions)}")
    print(f"📁 Raw data stored in: {collector.raw_data_dir}")
    
    if motions:
        print(f"\n📋 Sample motions:")
        for i, motion in enumerate(motions[:5]):
            content = motion['enriched_content']
            print(f"   {i+1}. {content['title'][:60]}...")
            print(f"      Type: {content['decision_type']}")
            print(f"      Date: {content['date'][:10] if content['date'] else 'Unknown'}")
            print(f"      Votes: {content['voting_count']}, Docs: {content['document_count']}")
            print()
    
    return motions

if __name__ == "__main__":
    main()