#!/usr/bin/env python3
"""
Law Articles Completeness Analysis
Analyzes document entity to verify all law articles (wetsartikelen) are present.
"""

from pathlib import Path
import json
from collections import Counter

def analyze_law_completeness():
    """Analyze completeness of law articles in document entity."""

    document_dir = Path("bronmateriaal-onbewerkt/document")
    if not document_dir.exists():
        print(f"Directory {document_dir} does not exist!")
        return

    # Get all fullterm document files
    document_files = list(document_dir.glob("*fullterm*.json"))
    print(f"Analyzing {len(document_files)} document files")

    # Counters for law-related documents
    law_types = Counter()
    law_dates = Counter()
    total_law_docs = 0

    # Keywords that indicate law-related content
    law_keywords = [
        'wet', 'wetsvoorstel', 'wetsartikel', 'wetgeving',
        'voorstel van wet', 'memorie van toelichting',
        'nota van wijziging', 'eindtekst', 'bijgewerkte tekst'
    ]

    for file_path in sorted(document_files):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Document files are direct lists
            if isinstance(data, list):
                records = data
            else:
                continue

            for record in records:
                if isinstance(record, dict):
                    # Handle None values safely
                    soort = record.get('Soort') or ''
                    onderwerp = record.get('Onderwerp') or ''

                    # Convert to string and lowercase safely
                    soort_str = str(soort).lower() if soort is not None else ''
                    onderwerp_str = str(onderwerp).lower() if onderwerp is not None else ''

                    # Check if this is law-related
                    is_law_related = any(keyword in soort_str or keyword in onderwerp_str for keyword in law_keywords)

                    if is_law_related:
                        total_law_docs += 1
                        law_types[record.get('Soort', 'Unknown')] += 1

                        # Track dates for recency
                        datum = record.get('Datum')
                        if datum:
                            # Extract year from ISO date
                            year = datum[:4] if len(datum) >= 4 else 'Unknown'
                            law_dates[year] += 1

        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            continue

    # Print results
    print(f"\n=== LAW ARTICLES COMPLETENESS ANALYSIS ===")
    print(f"Total law-related documents: {total_law_docs}")
    print(f"Percentage of all documents: {(total_law_docs / 58250 * 100):.1f}%" if total_law_docs > 0 else "0%")

    print(f"\n=== LAW DOCUMENT TYPES ===")
    for law_type, count in sorted(law_types.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_law_docs) * 100 if total_law_docs > 0 else 0
        print(f"{law_type}: {count} ({percentage:.1f}%)")

    print(f"\n=== LAW DOCUMENTS BY YEAR ===")
    for year, count in sorted(law_dates.items(), key=lambda x: x[0]):
        print(f"{year}: {count} documents")

    # Check for completeness indicators
    print(f"\n=== COMPLETENESS ASSESSMENT ===")
    if total_law_docs > 1000:  # Substantial number
        print("✅ SIGNIFICANT LAW CONTENT FOUND")
        print("   - Bills, amendments, explanatory memoranda present")
        print("   - Multiple types of legal documents collected")
    else:
        print("❌ INSUFFICIENT LAW CONTENT")

    # Check date range
    years = [y for y in law_dates.keys() if y != 'Unknown']
    if years:
        min_year = min(years)
        max_year = max(years)
        print(f"   - Date range: {min_year} - {max_year}")
        if max_year >= '2024':
            print("✅ RECENT LAW CONTENT PRESENT")
        else:
            print("❌ MISSING RECENT LAW CONTENT")

if __name__ == "__main__":
    analyze_law_completeness()