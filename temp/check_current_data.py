import json
import os
from datetime import datetime

# Check existing stemming data date range
stemming_dir = r'C:\motiematcher\bronmateriaal-onbewerkt\stemming_complete'
if os.path.exists(stemming_dir):
    files = [f for f in os.listdir(stemming_dir) if f.endswith('.json')]
    print(f'Found {len(files)} JSON files in stemming_complete')
    if files:
        all_dates = []
        total_records = 0

        for file in files[:3]:  # Check first 3 files
            try:
                with open(os.path.join(stemming_dir, file), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    total_records += len(data)
                    dates = [item.get('GewijzigdOp') for item in data if item.get('GewijzigdOp')]
                    all_dates.extend(dates)
                    print(f'File {file}: {len(data)} records')
            except Exception as e:
                print(f'Error reading {file}: {e}')
                continue

        if all_dates:
            all_dates.sort()
            print(f'Earliest stemming date: {all_dates[0]}')
            print(f'Latest stemming date: {all_dates[-1]}')
            print(f'Total records checked: {total_records}')
        else:
            print('No dates found in existing data')
    else:
        print('No JSON files found in stemming_complete directory')
else:
    print(f'stemming_complete directory does not exist at {stemming_dir}')