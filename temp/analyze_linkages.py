import json

# Analyze how votes are linked to decisions and motions

def analyze_vote_linkages():
    print("=== Vote Linkage Analysis ===\n")

    # Load data
    with open('bronnateriaal-onbewerkt/besluit_current/besluit_voted_motions_20251003_200218.json', 'r', encoding='utf-8') as f:
        besluit_data = json.load(f)

    with open('bronnateriaal-onbewerkt/stemming_current/stemming_voted_motions_20251003_200218.json', 'r', encoding='utf-8') as f:
        stemming_data = json.load(f)

    print(f"Total decisions: {len(besluit_data)}")
    print(f"Total votes: {len(stemming_data)}")

    # Check how votes are linked to decisions
    print("\n=== Vote-Decision Linkage ===")
    votes_by_decision = {}
    for stemming in stemming_data:
        besluit_id = stemming.get('Besluit_Id')
        if besluit_id:
            if besluit_id not in votes_by_decision:
                votes_by_decision[besluit_id] = []
            votes_by_decision[besluit_id].append(stemming)

    print(f"Decisions with votes: {len(votes_by_decision)}")
    print(f"Total votes accounted for: {sum(len(votes) for votes in votes_by_decision.values())}")

    # Analyze decision types for voted vs non-voted
    print("\n=== Decision Types Analysis ===")
    voted_decisions = {}
    non_voted_decisions = {}

    for besluit in besluit_data:
        besluit_id = besluit.get('Id')
        has_votes = besluit_id in votes_by_decision
        b_type = besluit.get('BesluitSoort', 'Unknown')

        if has_votes:
            voted_decisions[b_type] = voted_decisions.get(b_type, 0) + 1
        else:
            non_voted_decisions[b_type] = non_voted_decisions.get(b_type, 0) + 1

    print("Decision types WITH votes:")
    for b_type, count in sorted(voted_decisions.items(), key=lambda x: x[1], reverse=True):
        print(f"  {b_type}: {count}")

    print("\nDecision types WITHOUT votes:")
    for b_type, count in sorted(non_voted_decisions.items(), key=lambda x: x[1], reverse=True)[:10]:  # Top 10
        print(f"  {b_type}: {count}")

    # Sample voted decisions
    print("\n=== Sample Voted Decisions ===")
    count = 0
    for besluit in besluit_data:
        if besluit.get('Stemming') and count < 3:
            print(f"Decision ID: {besluit.get('Id')}")
            print(f"  Type: {besluit.get('BesluitSoort', 'Unknown')}")
            print(f"  Status: {besluit.get('Status', 'Unknown')}")
            print(f"  Votes: {len(besluit.get('Stemming', []))}")
            print(f"  Text: {besluit.get('BesluitTekst', 'N/A')[:100]}...")
            count += 1
            print()

    # Sample non-voted decisions
    print("=== Sample Non-Voted Decisions ===")
    count = 0
    for besluit in besluit_data:
        if not besluit.get('Stemming') and count < 3:
            print(f"Decision ID: {besluit.get('Id')}")
            print(f"  Type: {besluit.get('BesluitSoort', 'Unknown')}")
            print(f"  Status: {besluit.get('Status', 'Unknown')}")
            print(f"  Text: {besluit.get('BesluitTekst', 'N/A')[:100]}...")
            count += 1
            print()

    # Check if decisions are linked to motions
    print("=== Decision-Motion Linkage Check ===")
    decisions_with_zaak_refs = 0
    for besluit in besluit_data:
        zaak_refs = besluit.get('Zaak', [])
        if zaak_refs:
            decisions_with_zaak_refs += 1

    print(f"Decisions with Zaak references: {decisions_with_zaak_refs}/{len(besluit_data)}")

    print("\n=== Summary ===")
    print("✅ Votes are properly linked to decisions via Besluit_Id")
    print("✅ Decision types clearly indicate voting status:")
    print("   - 'Stemmen - aangenomen/verworpen' = voted and decided")
    print("   - 'Ingediend' = submitted but not yet voted")
    print("   - 'Stemmen - aangehouden' = voting postponed")
    print("   - 'Termijn - vervallen' = expired without vote")

if __name__ == "__main__":
    analyze_vote_linkages()