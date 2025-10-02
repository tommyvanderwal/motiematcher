"""
Direct Voting Fetcher - Start with voting records and work backwards to motions
"""

import requests
import json
from datetime import datetime
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DirectVotingFetcher:
    """Fetches voting records first, then finds associated decisions/motions"""
    
    def __init__(self):
        self.base_url = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MotieMatcher-DirectVoting/1.0',
            'Accept': 'application/json'
        })
    
    def get_recent_voting_records(self, limit=100):
        """Get recent voting records with actual votes"""
        logger.info(f"Fetching {limit} recent voting records...")
        
        url = f"{self.base_url}/Stemming"
        
        params = {
            '$filter': "Soort ne null and ActorNaam ne null and Besluit_Id ne null",
            '$top': limit,
            '$orderby': 'GewijzigdOp desc',
            '$select': 'Id,Besluit_Id,Soort,FractieGrootte,ActorNaam,ActorFractie,GewijzigdOp'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                votes = data.get('value', [])
                logger.info(f"Found {len(votes)} voting records")
                return votes
            else:
                logger.error(f"Error fetching votes: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Exception fetching votes: {e}")
            return []
    
    def get_decision_details(self, decision_id):
        """Get details for a specific decision"""
        url = f"{self.base_url}/Besluit(guid'{decision_id}')"
        
        params = {
            '$select': 'Id,BesluitSoort,BesluitTekst,Status,GewijzigdOp,Agendapunt_Id'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=20)
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            logger.debug(f"Error fetching decision {decision_id}: {e}")
            return None
    
    def group_votes_by_decision(self, votes):
        """Group voting records by decision ID"""
        decisions_votes = {}
        
        for vote in votes:
            decision_id = vote.get('Besluit_Id')
            if decision_id:
                if decision_id not in decisions_votes:
                    decisions_votes[decision_id] = []
                decisions_votes[decision_id].append(vote)
        
        logger.info(f"Found votes for {len(decisions_votes)} different decisions")
        return decisions_votes
    
    def fetch_motions_with_real_voting(self, count=20):
        """Fetch real motions with voting data by starting with votes"""
        logger.info(f"=== Fetching {count} real decisions with voting ===")
        
        results = {
            'metadata': {
                'fetched_at': datetime.now().isoformat(),
                'api_base': self.base_url,
                'total_requested': count
            },
            'motions': []
        }
        
        # 1. Get recent voting records
        votes = self.get_recent_voting_records(500)  # Get more to have choices
        
        if not votes:
            logger.error("No voting records found!")
            return results
        
        # 2. Group by decision
        decisions_votes = self.group_votes_by_decision(votes)
        
        # 3. Process each decision with voting
        motion_count = 0
        
        for decision_id, decision_votes in decisions_votes.items():
            if motion_count >= count:
                break
            
            # Get decision details
            decision = self.get_decision_details(decision_id)
            
            if decision:
                motion_data = {
                    'id': decision_id,
                    'type': 'besluit_met_stemming',
                    'title': decision.get('BesluitTekst', 'Onbekend besluit'),
                    'decision_type': decision.get('BesluitSoort', 'Onbekend'),
                    'status': decision.get('Status', 'Onbekend'),
                    'date': decision.get('GewijzigdOp', ''),
                    'voting_records': []
                }
                
                # Process votes for this decision
                vote_summary = {'voor': 0, 'tegen': 0, 'onthouding': 0}
                
                for vote in decision_votes:
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
                        'vote_date': vote.get('GewijzigdOp', '')
                    }
                    
                    motion_data['voting_records'].append(vote_record)
                
                motion_data['total_votes_voor'] = vote_summary['voor']
                motion_data['total_votes_tegen'] = vote_summary['tegen'] 
                motion_data['total_votes_onthouding'] = vote_summary['onthouding']
                motion_data['enrichment_status'] = 'completed'
                
                results['motions'].append(motion_data)
                motion_count += 1
                
                logger.info(f"Added decision {motion_count}/{count}: {motion_data['title'][:60]}...")
                logger.info(f"  Votes: {len(decision_votes)} parties voted")
            
            # Small delay
            time.sleep(0.1)
        
        results['metadata']['actual_fetched'] = len(results['motions'])
        
        return results

def main():
    """Main execution function"""
    fetcher = DirectVotingFetcher()
    
    # Fetch 20 real decisions with voting data
    results = fetcher.fetch_motions_with_real_voting(20)
    
    # Save results
    output_file = 'output/real_decisions_with_voting.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print(f"\n✅ Fetched {len(results['motions'])} real decisions with voting data")
    print(f"📁 Saved to: {output_file}")
    
    if results['motions']:
        print(f"\n📊 Sample decisions:")
        for i, motion in enumerate(results['motions'][:3]):
            print(f"   {i+1}. {motion['title'][:70]}...")
            print(f"      Votes: {motion['total_votes_voor']} voor, {motion['total_votes_tegen']} tegen, {motion['total_votes_onthouding']} onthouding")
            print(f"      Parties: {len(motion['voting_records'])}")
    
    return results

if __name__ == "__main__":
    main()