import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.main_simple import get_motions

from collections import Counter

# Additional grouping diagnostics using raw data
RAW_DATA = BASE_DIR / "final_linked_data.json"

if RAW_DATA.exists():
    import json
    with RAW_DATA.open("r", encoding="utf-8") as handle:
        raw_records = json.load(handle)

    counts = Counter(record.get("Besluit_Id") for record in raw_records)
    print("unique motions in raw data:", len(counts))
    for motion_id, amount in counts.most_common(5):
        print(f"motion {motion_id}: {amount} records")

motions = get_motions()
print(f"motions: {len(motions)}")
for motion in motions:
    print("\n--- motion ---")
    print("id", motion['id'])
    print("onderwerp", motion['onderwerp'])
    print("stem records", len(motion['stemverdeling']))
    sample = motion['stemverdeling'][:5]
    for record in sample:
        print(record)
