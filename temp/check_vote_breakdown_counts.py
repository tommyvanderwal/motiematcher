import json
from collections import Counter
from pathlib import Path

path = Path("bronmateriaal-onbewerkt/current/motion_index/motions_enriched.json")
records = json.loads(path.read_text(encoding="utf-8"))
counts = Counter()
for idx, record in enumerate(records[:1000]):
    votes = record.get("vote_breakdown") or []
    counts[len(votes)] += 1

print("Unique vote_breakdown lengths (first 1000 motions):")
for length, freq in counts.most_common(10):
    print(f"  {length}: {freq}")

sample = records[0]
print(f"First motion vote entries: {len(sample.get('vote_breakdown') or [])}")
print("First 5 vote entries:")
for entry in (sample.get("vote_breakdown") or [])[:5]:
    print(entry)
