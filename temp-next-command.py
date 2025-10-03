import json

# Check what types of zaken are in the 30-day data using the Soort field
with open('zaak/zaak_page_1_30days_20251002_201700.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    # Handle both list and dict formats
    if isinstance(data, list):
        zaken = data
    else:
        zaken = data.get('value', [])

    print(f'Total zaken in first file: {len(zaken)}')

    # Check all unique Soort values
    types = {}
    votable_types = ['Motie', 'Wet', 'Amendement']
    votable_count = 0

    for zaak in zaken:
        soort = zaak.get('Soort', 'Unknown')
        types[soort] = types.get(soort, 0) + 1
        if soort in votable_types:
            votable_count += 1

    print('\nZaak soorten:')
    for t, count in sorted(types.items()):
        marker = ' <-- VOTABLE' if t in votable_types else ''
        print(f'{t}: {count}{marker}')

    print(f'\nVotable zaken in this file: {votable_count}')

    # Check a few more files to get better overview
    import os
    zaak_files = [f for f in os.listdir('zaak') if '_30days_' in f and f.endswith('.json')]
    print(f'\nFound {len(zaak_files)} 30-day zaak files')

    total_zaken = 0
    total_votable = 0
    all_types = {}

    for filename in zaak_files[:5]:  # Check first 5 files
        try:
            with open(f'zaak/{filename}', 'r', encoding='utf-8') as f:
                file_data = json.load(f)
                if isinstance(file_data, list):
                    file_zaken = file_data
                else:
                    file_zaken = file_data.get('value', [])

                total_zaken += len(file_zaken)
                for zaak in file_zaken:
                    soort = zaak.get('Soort', 'Unknown')
                    all_types[soort] = all_types.get(soort, 0) + 1
                    if soort in votable_types:
                        total_votable += 1
        except Exception as e:
            print(f'Error reading {filename}: {e}')

    print(f'\nOverview of first 5 files:')
    print(f'Total zaken: {total_zaken}')
    print(f'Total votable: {total_votable}')
    print('\nAll zaak soorten across files:')
    for t, count in sorted(all_types.items(), key=lambda x: (x[0] is None, x[0] or '')):
        marker = ' <-- VOTABLE' if t in votable_types else ''
        print(f'{t}: {count}{marker}')