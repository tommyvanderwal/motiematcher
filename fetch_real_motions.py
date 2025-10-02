"""
Real Motion Fetcher - Haalt echte moties met stemmingen op van Tweede Kamer API
"""

import requests
import json
from datetime import datetime
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealMotionFetcher:
    """Fetches real motions with voting data from Dutch Parliament API"""
    
    def __init__(self):
        self.base_url = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MotieMatcher-RealFetcher/1.0',
            'Accept': 'application/json'
        })
    
    def find_motion_activities(self, limit=20):
        """Find activities that are motions"""
        logger.info("Searching for motion activities...")
        
        url = f"{self.base_url}/Activiteit"
        
        # Search for activities containing 'motie' in different fields
        filters = [
            "contains(tolower(Soort), 'motie')",
            "contains(tolower(Onderwerp), 'motie')"
        ]
        
        params = {
            '$filter': f"({' or '.join(filters)}) and Datum ge 2020-01-01T00:00:00Z",
            '$top': limit,
            '$orderby': 'Datum desc',
            '$select': 'Id,Soort,Nummer,Onderwerp,Datum,Status,Vergaderjaar'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            logger.info(f"Motion search status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                activities = data.get('value', [])
                logger.info(f"Found {len(activities)} motion activities")
                
                return activities
            else:
                logger.error(f"Error fetching motions: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Exception fetching motions: {e}")
            return []
    
    def find_decisions_for_activity(self, activity_id):
        """Find decisions (Besluit) for a specific activity"""
        logger.info(f"Searching decisions for activity: {activity_id}")
        
        url = f"{self.base_url}/Besluit"
        
        # Try to find decisions linked to this activity
        # Note: Need to explore the relationship structure
        params = {
            '$filter': f"Agendapunt/any(a: a/Activiteit_Id eq guid'{activity_id}')",
            '$select': 'Id,BesluitSoort,BesluitTekst,Status',
            '$top': 10
        }
        
        try:
            response = self.session.get(url, params=params, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                decisions = data.get('value', [])
                logger.info(f"Found {len(decisions)} decisions for activity {activity_id}")
                return decisions
            else:
                logger.info(f"No decisions found for activity {activity_id} (status: {response.status_code})")
                return []
                
        except Exception as e:
            logger.info(f"Error finding decisions for {activity_id}: {e}")
            return []
    
    def find_all_recent_decisions_with_voting(self, limit=100):
        """Find recent decisions that have voting records"""
        logger.info("Searching for recent decisions...")
        
        url = f"{self.base_url}/Besluit"
        
        params = {
            '$top': limit,
            '$orderby': 'GewijzigdOp desc',
            '$select': 'Id,BesluitSoort,BesluitTekst,Status,GewijzigdOp'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                decisions = data.get('value', [])
                logger.info(f"Found {len(decisions)} recent decisions")
                
                # Return all decisions - we'll check for voting later
                return decisions
                
        except Exception as e:
            logger.error(f"Error fetching decisions: {e}")
            return []
    
    def get_voting_for_decision(self, decision_id):
        """Get voting records for a specific decision"""
        logger.info(f"Fetching voting for decision: {decision_id}")
        
        url = f"{self.base_url}/Stemming"
        
        params = {
            '$filter': f"Besluit_Id eq guid'{decision_id}'",
            '$select': 'Id,Soort,FractieGrootte,ActorNaam,ActorFractie,Fractie_Id',
            '$orderby': 'ActorNaam'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                votes = data.get('value', [])
                logger.info(f"Found {len(votes)} votes for decision {decision_id}")
                return votes
            else:
                logger.info(f"No votes found for decision {decision_id}")
                return []
                
        except Exception as e:
            logger.info(f"Error fetching votes for {decision_id}: {e}")
            return []
    
    def get_current_parties(self):
        """Get current active political parties"""
        logger.info("Fetching current political parties...")
        
        url = f"{self.base_url}/Fractie"
        
        params = {
            '$filter': "DatumInactief eq null and NaamNL ne null",
            '$select': 'Id,Afkorting,NaamNL,AantalZetels',
            '$orderby': 'NaamNL'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                parties = data.get('value', [])
                logger.info(f"Found {len(parties)} active parties")
                return parties
                
        except Exception as e:
            logger.error(f"Error fetching parties: {e}")
            return []
    
    def fetch_motions_with_voting(self, count=20):
        """Main function to fetch motions with their voting data"""
        logger.info(f"=== Fetching {count} real motions with voting data ===")
        
        results = {
            'metadata': {
                'fetched_at': datetime.now().isoformat(),
                'api_base': self.base_url,
                'total_requested': count
            },
            'parties': [],
            'motions': []
        }
        
        # 1. Get current parties
        parties = self.get_current_parties()
        results['parties'] = parties
        
        # 2. Search for recent decisions with voting (more reliable approach)
        decisions = self.find_all_recent_decisions_with_voting(50)
        
        motion_count = 0
        
        for decision in decisions:
            if motion_count >= count:
                break
                
            # 3. Get voting data for this decision
            votes = self.get_voting_for_decision(decision['Id'])
            
            if votes:  # Only include if there's voting data
                motion_data = {
                    'id': decision['Id'],
                    'type': 'besluit_met_stemming',
                    'title': decision.get('BesluitTekst', 'Onbekend besluit'),
                    'decision_type': decision.get('BesluitSoort', 'Onbekend'),
                    'status': decision.get('Status', 'Onbekend'),
                    'date': decision.get('GewijzigdOp', ''),
                    'voting_records': []
                }
                
                # Process votes
                vote_summary = {'voor': 0, 'tegen': 0, 'onthouding': 0}
                
                for vote in votes:
                    vote_type = vote.get('Soort', '').lower()
                    
                    # Map Dutch vote types
                    if vote_type == 'voor':
                        mapped_vote = 'voor'
                    elif vote_type == 'tegen':
                        mapped_vote = 'tegen'
                    else:
                        mapped_vote = 'onthouding'
                    
                    if mapped_vote in vote_summary:
                        vote_summary[mapped_vote] += 1
                    
                    vote_record = {
                        'party_name': vote.get('ActorNaam', 'Onbekend'),
                        'party_abbreviation': vote.get('ActorFractie', 'Onbekend'),
                        'vote': mapped_vote,
                        'num_members': vote.get('FractieGrootte', 0),
                        'vote_date': decision.get('GewijzigdOp', '')
                    }
                    
                    motion_data['voting_records'].append(vote_record)
                
                motion_data['total_votes_voor'] = vote_summary['voor']
                motion_data['total_votes_tegen'] = vote_summary['tegen'] 
                motion_data['total_votes_onthouding'] = vote_summary['onthouding']
                motion_data['enrichment_status'] = 'completed'
                
                results['motions'].append(motion_data)
                motion_count += 1
                
                logger.info(f"Added motion {motion_count}/{count}: {motion_data['title'][:50]}...")
                
            # Small delay to be nice to the API
            time.sleep(0.2)
        
        results['metadata']['actual_fetched'] = len(results['motions'])
        
        return results

def main():
    """Main execution function"""
    fetcher = RealMotionFetcher()
    
    # Fetch 20 real motions with voting
    results = fetcher.fetch_motions_with_voting(20)
    
    # Save results
    output_file = 'output/real_motions_with_voting.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print(f"\n✅ Fetched {len(results['motions'])} real motions with voting data")
    print(f"📁 Saved to: {output_file}")
    print(f"🏛️ Found {len(results['parties'])} active parties")
    
    if results['motions']:
        print(f"\n📊 Sample motion:")
        sample = results['motions'][0]
        print(f"   Title: {sample['title'][:80]}...")
        print(f"   Votes: {sample['total_votes_voor']} voor, {sample['total_votes_tegen']} tegen, {sample['total_votes_onthouding']} onthouding")
        print(f"   Parties voted: {len(sample['voting_records'])}")

if __name__ == "__main__":
    main()