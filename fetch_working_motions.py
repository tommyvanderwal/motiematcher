"""
Working Real Motions Fetcher - Now with proper understanding of the API structure
"""

import requests
import json
from datetime import datetime
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkingMotionsFetcher:
    """Fetches real motions with voting data using proper API queries"""
    
    def __init__(self):
        self.base_url = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MotieMatcher-WorkingFetcher/1.0',
            'Accept': 'application/json'
        })
    
    def get_recent_voting_records(self, limit=50):
        """Get recent voting records"""
        logger.info(f"Fetching {limit} recent voting records...")
        
        url = f"{self.base_url}/Stemming"
        
        params = {
            '$top': limit,
            '$orderby': 'GewijzigdOp desc',
            '$expand': 'Besluit,Fractie'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                votes = data.get('value', [])
                logger.info(f"✅ Found {len(votes)} voting records")
                return votes
            else:
                logger.error(f"❌ Error fetching votes: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Exception fetching votes: {e}")
            return []
    
    def group_votes_by_decision(self, votes):
        """Group voting records by decision ID"""
        decisions = {}
        
        for vote in votes:
            decision_id = vote.get('Besluit_Id')
            if decision_id:
                if decision_id not in decisions:
                    decisions[decision_id] = {
                        'decision_id': decision_id,
                        'votes': []
                    }
                decisions[decision_id]['votes'].append(vote)
        
        logger.info(f"Found votes for {len(decisions)} different decisions")
        return decisions
    
    def fetch_real_motions_with_voting(self, count=20):
        """Fetch real motions with voting data"""
        logger.info(f"=== Fetching {count} real motions with voting ===")
        
        results = {
            'metadata': {
                'fetched_at': datetime.now().isoformat(),
                'api_base': self.base_url,
                'total_requested': count
            },
            'motions': []
        }
        
        # 1. Get voting records
        votes = self.get_recent_voting_records(200)  # Get more to have choice
        
        if not votes:
            logger.error("No voting records found!")
            return results
        
        # 2. Group by decision
        decisions = self.group_votes_by_decision(votes)
        
        # 3. Process each decision with voting
        motion_count = 0
        
        for decision_id, decision_data in list(decisions.items())[:count]:
            decision_votes = decision_data['votes']
            
            # Get decision info from first vote (they all have the same decision)
            first_vote = decision_votes[0]
            besluit_info = first_vote.get('Besluit', {})
            
            motion = {
                'id': decision_id,
                'type': 'besluit_met_stemming',
                'title': besluit_info.get('BesluitTekst', 'Besluit zonder titel'),
                'decision_type': besluit_info.get('BesluitSoort', 'Onbekend'),
                'decision_status': besluit_info.get('Status', 'Onbekend'),
                'voting_type': besluit_info.get('StemmingsSoort', 'Onbekend'),
                'date': first_vote.get('GewijzigdOp', ''),
                'voting_records': [],
                'vote_summary': {'voor': 0, 'tegen': 0, 'onthouding': 0}
            }
            
            # Process all votes for this decision
            parties_voted = set()
            
            for vote in decision_votes:
                vote_type = vote.get('Soort', '').lower()
                party_name = vote.get('ActorNaam', 'Onbekend')
                
                # Map vote types
                if vote_type == 'voor':
                    mapped_vote = 'voor'
                elif vote_type == 'tegen':
                    mapped_vote = 'tegen'
                else:
                    mapped_vote = 'onthouding'
                
                # Add to summary
                if mapped_vote in motion['vote_summary']:
                    motion['vote_summary'][mapped_vote] += 1
                
                vote_record = {
                    'party_name': party_name,
                    'party_abbreviation': vote.get('ActorFractie', party_name),
                    'vote': mapped_vote,
                    'num_members': vote.get('FractieGrootte', 0),
                    'vote_date': vote.get('GewijzigdOp', ''),
                    'is_correction': vote.get('Vergissing', False)
                }
                
                motion['voting_records'].append(vote_record)
                parties_voted.add(party_name)
            
            # Set enrichment status
            motion['enrichment_status'] = 'completed'
            motion['parties_count'] = len(parties_voted)
            
            results['motions'].append(motion)
            motion_count += 1
            
            logger.info(f"✅ Motion {motion_count}/{count}: {motion['title'][:60]}...")
            logger.info(f"   Votes: {motion['vote_summary']['voor']} voor, {motion['vote_summary']['tegen']} tegen, {motion['vote_summary']['onthouding']} onthouding")
            logger.info(f"   Parties: {len(parties_voted)}")
            
            time.sleep(0.1)  # Be nice to the API
        
        results['metadata']['actual_fetched'] = len(results['motions'])
        
        return results

def main():
    """Main execution function"""
    fetcher = WorkingMotionsFetcher()
    
    # Fetch 20 real motions with voting data
    results = fetcher.fetch_real_motions_with_voting(20)
    
    # Save results
    output_file = 'output/real_motions_with_voting_v2.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print(f"\n🎉 SUCCESS! Fetched {len(results['motions'])} real motions with voting data!")
    print(f"📁 Saved to: {output_file}")
    
    if results['motions']:
        print(f"\n📊 Sample motions:")
        for i, motion in enumerate(results['motions'][:5]):
            print(f"   {i+1}. {motion['title'][:70]}...")
            print(f"      Type: {motion['decision_type']}")
            print(f"      Votes: {motion['vote_summary']['voor']} voor, {motion['vote_summary']['tegen']} tegen, {motion['vote_summary']['onthouding']} onthouding")
            print(f"      Parties: {motion['parties_count']}")
            print()
    
    return results

if __name__ == "__main__":
    main()