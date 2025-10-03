#!/usr/bin/env python3
"""
Debug Stemming Data Structure
Check what the voting data actually looks like.
"""

from pathlib import Path
import json

def debug_stemming_structure():
    """Debug the stemming data structure."""

    stemming_dir = Path("bronmateriaal-onbewerkt/stemming")
    if not stemming_dir.exists():
        print(f"Directory {stemming_dir} does not exist!")
        return

    stemming_files = list(stemming_dir.glob("*fullterm*.json"))
    print(f"Found {len(stemming_files)} stemming files")

    # Sample first few files
    sample_files = stemming_files[:3]

    for file_path in sample_files:
        print(f"\n=== ANALYZING {file_path.name} ===")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            print(f"Data type: {type(data)}")

            if isinstance(data, dict):
                print(f"Keys: {list(data.keys())}")

                if 'value' in data:
                    records = data['value']
                    print(f"Records in 'value': {len(records)}")

                    # Sample first few records
                    for i, record in enumerate(records[:3]):
                        if isinstance(record, dict):
                            print(f"Record {i+1} keys: {list(record.keys())}")
                            print(f"Record {i+1} sample data: {dict(list(record.items())[:5])}")
                            print()

            elif isinstance(data, list):
                print(f"Direct list with {len(data)} records")

                # Sample first few records
                for i, record in enumerate(data[:3]):
                    if isinstance(record, dict):
                        print(f"Record {i+1} keys: {list(record.keys())}")
                        print(f"Record {i+1} sample data: {dict(list(record.items())[:5])}")
                        print()

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    debug_stemming_structure()