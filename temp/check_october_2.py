import json
from datetime import datetime

# Check if motions from October 2, 2025 have voting results in our data

def check_october_2_votes():
    print("=== Checking October 2, 2025 Voting Results ===\n")

    # Load data
    with open('bronnateriaal-onbewerkt/stemming_current/stemming_voted_motions_20251003_200218.json', 'r', encoding='utf-8') as f:
        stemming_data = json.load(f)

    with open('bronnateriaal-onbewerkt/besluit_current/besluit_voted_motions_20251003_200218.json', 'r', encoding='utf-8') as f:
        besluit_data = json.load(f)

    print(f"Total votes in dataset: {len(stemming_data)}")
    print(f"Total decisions in dataset: {len(besluit_data)}")

    # Filter votes from October 2, 2025
    october_2_votes = []
    for stemming in stemming_data:
        gewijzigd_op = stemming.get('GewijzigdOp', '')
        if gewijzigd_op.startswith('2025-10-02'):
            october_2_votes.append(stemming)

    print(f"\nVotes from October 2, 2025: {len(october_2_votes)}")

    if october_2_votes:
        # Group by decision
        votes_by_decision = {}
        for vote in october_2_votes:
            besluit_id = vote.get('Besluit_Id')
            if besluit_id:
                if besluit_id not in votes_by_decision:
                    votes_by_decision[besluit_id] = []
                votes_by_decision[besluit_id].append(vote)

        print(f"Decisions voted on October 2: {len(votes_by_decision)}")

        # Show sample votes
        print("\nSample votes from October 2:")
        for i, vote in enumerate(october_2_votes[:10]):
            fractie = vote.get('ActorFractie', 'Unknown')
            soort = vote.get('Soort', 'Unknown')
            tijd = vote.get('GewijzigdOp', 'Unknown')
            print(f"  {i+1}. {fractie}: {soort} at {tijd}")

        # Check decision details for October 2
        print("\nDecision details for October 2 votes:")
        for besluit_id, votes in list(votes_by_decision.items())[:3]:  # First 3 decisions
            # Find the decision
            decision = None
            for besluit in besluit_data:
                if besluit.get('Id') == besluit_id:
                    decision = besluit
                    break

            if decision:
                print(f"Decision {besluit_id}:")
                print(f"  Type: {decision.get('BesluitSoort', 'Unknown')}")
                print(f"  Status: {decision.get('Status', 'Unknown')}")
                print(f"  Votes: {len(votes)} parties")
                print(f"  Text: {decision.get('BesluitTekst', 'N/A')[:80]}...")

                # Show vote breakdown
                voor_count = sum(1 for v in votes if v.get('Soort') == 'Voor')
                tegen_count = sum(1 for v in votes if v.get('Soort') == 'Tegen')
                print(f"  Result: {voor_count} Voor, {tegen_count} Tegen")
                print()

    else:
        print("❌ No votes found from October 2, 2025 in the dataset")

    # Check if there are any decisions from October 2 without votes
    print("\n=== Checking for October 2 Decisions Without Votes ===")
    october_2_decisions = []
    for besluit in besluit_data:
        gewijzigd_op = besluit.get('GewijzigdOp', '')
        if gewijzigd_op.startswith('2025-10-02'):
            october_2_decisions.append(besluit)

    print(f"Total decisions from October 2: {len(october_2_decisions)}")

    voted_decisions = len(votes_by_decision) if 'votes_by_decision' in locals() else 0
    non_voted_decisions = len(october_2_decisions) - voted_decisions

    print(f"Decisions with votes: {voted_decisions}")
    print(f"Decisions without votes: {non_voted_decisions}")

    if non_voted_decisions > 0:
        print("\nSample non-voted decisions from October 2:")
        count = 0
        for besluit in october_2_decisions:
            if not besluit.get('Stemming') and count < 3:
                print(f"  {besluit.get('BesluitSoort', 'Unknown')} - {besluit.get('Status', 'Unknown')}")
                count += 1

    print("\n=== Summary ===")
    if october_2_votes:
        print("✅ October 2 motions have voting results in the dataset")
        print(f"   - {len(october_2_votes)} individual votes recorded")
        print(f"   - {len(votes_by_decision)} decisions with complete party breakdowns")
    else:
        print("❌ No October 2 voting data found - may need to re-collect")

if __name__ == "__main__":
    check_october_2_votes()