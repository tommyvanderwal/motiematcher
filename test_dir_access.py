#!/usr/bin/env python3
"""
Quick test script to check directory access
"""

import os
from pathlib import Path

print('Current dir:', os.getcwd())

# Try different approaches
test_paths = [
    r'C:\motiematcher\bronnateriaal-onbewerkt',
    r'C:\motiematcher\bronnateriaal-onbewerkt\zaak',
    'bronnateriaal-onbewerkt',
    'bronnateriaal-onbewerkt\\zaak',
    Path('bronnateriaal-onbewerkt'),
    Path('bronnateriaal-onbewerkt') / 'zaak'
]

for path in test_paths:
    try:
        exists = os.path.exists(str(path)) if not isinstance(path, Path) else path.exists()
        print(f'{path}: exists = {exists}')
    except Exception as e:
        print(f'{path}: ERROR = {e}')

# Try to list the directory directly
try:
    bron_path = Path('bronnateriaal-onbewerkt')
    print(f'Path object: {bron_path}')
    print(f'Path exists: {bron_path.exists()}')
    print(f'Path is_dir: {bron_path.is_dir()}')

    if bron_path.exists():
        contents = list(bron_path.iterdir())
        print(f'Contents: {len(contents)} items')
        print(f'First few: {[str(x) for x in contents[:3]]}')

        zaak_path = bron_path / 'zaak'
        print(f'Zaak path: {zaak_path}')
        print(f'Zaak exists: {zaak_path.exists()}')
        if zaak_path.exists():
            zaak_files = list(zaak_path.glob('*_30days_*.json'))
            print(f'30-day files found: {len(zaak_files)}')
            print(f'Examples: {[str(f.name) for f in zaak_files[:2]]}')

except Exception as e:
    print(f'Pathlib error: {e}')

# Check if it's a permission issue
try:
    import stat
    bron_stat = os.stat('bronnateriaal-onbewerkt')
    print(f'Directory stat: {stat.filemode(bron_stat.st_mode)}')
except Exception as e:
    print(f'Stat error: {e}')