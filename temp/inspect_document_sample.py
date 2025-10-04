import json
from pathlib import Path

def main():
    document_dir = Path('bronmateriaal-onbewerkt/document')
    files = sorted(document_dir.glob('document_page_*_fullterm_*.json'))
    if not files:
        print('No document files found')
        return

    file_path = files[0]

    try:
        with file_path.open('r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f'File not found: {file_path}')
        return
    except json.JSONDecodeError as exc:
        print(f'Invalid JSON in {file_path}: {exc}')
        return

    if not data:
        print('No records found')
        return

    print(f'Total records: {len(data)}')
    record = data[0]
    print('Keys:', sorted(record.keys()))
    for key in sorted(record.keys()):
        value = record[key]
        if isinstance(value, str) and len(value) > 200:
            value = value[:200] + '...'
        print(f'{key}: {value}')

if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'Unexpected error: {exc}')
