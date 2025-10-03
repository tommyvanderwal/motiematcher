#!/usr/bin/env python3
"""
Complete Document Analysis Script
Analyzes all document files to understand their structure and content types.
Handles the direct list structure (not wrapped in 'value' key like zaak files).
"""

import json
from pathlib import Path
from collections import Counter

def analyze_document_files():
    """Analyze all document files in the bronmateriaal-onbewerkt/document directory."""

    document_dir = Path("bronmateriaal-onbewerkt/document")
    if not document_dir.exists():
        print(f"Directory {document_dir} does not exist!")
        return

    # Get all fullterm document files
    document_files = list(document_dir.glob("*fullterm*.json"))
    print(f"Found {len(document_files)} document files")

    if not document_files:
        print("No document files found!")
        return

    total_records = 0
    all_document_types = Counter()
    sample_records = []

    for file_path in sorted(document_files):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Document files are direct lists, not wrapped in {'value': [...]}
            if isinstance(data, list):
                records = data
            else:
                print(f"Unexpected data structure in {file_path}: {type(data)}")
                continue

            total_records += len(records)

            # Analyze document types
            for record in records:
                if isinstance(record, dict):
                    doc_type = record.get('Soort', 'Unknown')
                    all_document_types[doc_type] += 1

                    # Collect sample records for inspection
                    if len(sample_records) < 5:
                        sample_records.append({
                            'file': file_path.name,
                            'record': record
                        })

        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            continue

    # Print results
    print(f"\n=== DOCUMENT ANALYSIS RESULTS ===")
    print(f"Total document records: {total_records}")
    print(f"Files processed: {len(document_files)}")

    print(f"\n=== DOCUMENT TYPES DISTRIBUTION ===")
    for doc_type, count in sorted(all_document_types.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_records) * 100 if total_records > 0 else 0
        print(f"{doc_type}: {count} ({percentage:.1f}%)")

    print(f"\n=== SAMPLE RECORDS ===")
    for i, sample in enumerate(sample_records, 1):
        print(f"\n--- Sample {i} from {sample['file']} ---")
        record = sample['record']
        print(f"ID: {record.get('Id', 'N/A')}")
        print(f"Soort: {record.get('Soort', 'N/A')}")
        print(f"Onderwerp: {record.get('Onderwerp', 'N/A')[:100]}..." if record.get('Onderwerp') else "Onderwerp: N/A")
        print(f"Datum: {record.get('Datum', 'N/A')}")

        # Check for law-related content
        if 'wet' in str(record.get('Soort', '')).lower() or 'wet' in str(record.get('Onderwerp', '')).lower():
            print("*** POTENTIAL LAW CONTENT ***")

if __name__ == "__main__":
    analyze_document_files()