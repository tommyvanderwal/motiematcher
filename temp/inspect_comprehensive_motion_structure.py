import json
from pathlib import Path

PATH = Path(r"c:\motiematcher\bronmateriaal-onbewerkt\comprehensive_motion_56e10506_20251002_192333.json")


def main() -> None:
    with PATH.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    print(f"Top-level keys: {list(data.keys())}")
    motion = data.get("motion")
    if isinstance(motion, dict):
        print(f"Motion keys: {list(motion.keys())[:20]}")
    decision = data.get("decision")
    if isinstance(decision, dict):
        print(f"Decision keys: {list(decision.keys())[:20]}")
        votes = decision.get("_votes")
        if isinstance(votes, list):
            print(f"Votes count: {len(votes)}")
            if votes:
                print(f"Vote sample keys: {list(votes[0].keys())}")
    documents = data.get("documents")
    if isinstance(documents, list):
        print(f"Documents: {len(documents)} entries")
        if documents:
            doc = documents[0]
            print(f"Document keys: {list(doc.keys())[:20]}")
            content = doc.get("text")
            if isinstance(content, str):
                print(f"Document text length: {len(content)}")


if __name__ == "__main__":
    main()
