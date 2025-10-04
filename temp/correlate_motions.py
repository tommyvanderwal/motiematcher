import json
from pathlib import Path

# Load scraped motion data
with open('temp/scraped_motion_votes.json', 'r', encoding='utf-8') as f:
    scraped_motions = json.load(f)

# Extract motion IDs
motion_ids = []
for motion in scraped_motions:
    url = motion['url']
    # Extract id from URL: id=2025Z13886
    if 'id=' in url:
        id_part = url.split('id=')[1].split('&')[0]
        motion_ids.append(id_part)

print(f"Found {len(motion_ids)} motion IDs: {motion_ids}")

# Search zaak files for these motions
zaak_dir = Path("c:/motiematcher/bronmateriaal-onbewerkt/zaak")
found_motions = {}

for file in sorted(zaak_dir.glob("*.json")):
    with file.open("r", encoding="utf-8") as f:
        data = json.load(f)
    records = data if isinstance(data, list) else data.get("value", [])
    for record in records:
        nummer = record.get('Nummer')
        if nummer in motion_ids:
            found_motions[nummer] = record
            print(f"Found motion {nummer} in {file.name}")

# Now check enriched data
enriched_file = Path("c:/motiematcher/step1_fullterm_filtered_enriched_data.json")
if enriched_file.exists():
    with enriched_file.open("r", encoding="utf-8") as f:
        enriched_data = json.load(f)

    enriched_motions = {}
    zaken_list = enriched_data.get('zaken', [])
    for item in zaken_list:
        if isinstance(item, dict):
            zaak = item.get('zaak', {})
            nummer = zaak.get('Nummer')
            if nummer in motion_ids:
                enriched_motions[nummer] = item
                print(f"Found enriched motion {nummer}")
        else:
            print(f"Unexpected item type in zaken: {type(item)}")

# Correlate
results = []
for mid in motion_ids:
    result = {
        'motion_id': mid,
        'zaak_data': found_motions.get(mid),
        'enriched_data': enriched_motions.get(mid),
        'has_votes_in_enriched': bool(enriched_motions.get(mid, {}).get('voting_data'))
    }
    results.append(result)

# Save correlation
with open('temp/motion_correlation.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"Saved correlation to temp/motion_correlation.json")