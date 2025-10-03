#!/usr/bin/env python3
"""
Complete document analysis to find laws and legal documents.
Analyzes all document files to identify document types and locate wetten/wetsartikelen.
"""

import json
from pathlib import Path
from collections import Counter

def analyze_all_documents():
    """Analyze all document files to find document types and locate laws."""

    # Find all document files
    doc_dir = Path("bronmateriaal-onbewerkt/document")
    doc_files = list(doc_dir.glob("*fullterm*.json"))

    print(f"Found {len(doc_files)} document files")

    # Counters for analysis
    total_docs = 0
    doc_types = Counter()
    doc_soorten = Counter()
    doc_categories = Counter()

    # Sample some documents for detailed analysis
    sample_docs = []

    for file_path in sorted(doc_files):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Process each document in the file
            for doc in data.get('value', []):
                total_docs += 1

                # Collect document types
                doc_type = doc.get('Soort', 'Unknown')
                doc_soorten[doc_type] += 1

                # Collect categories if available
                category = doc.get('Categorie', 'Unknown')
                doc_categories[category] += 1

                # Collect document types (different field)
                doc_type_field = doc.get('DocumentType', 'Unknown')
                doc_types[doc_type_field] += 1

                # Sample first few documents for detailed inspection
                if len(sample_docs) < 10:
                    sample_docs.append({
                        'id': doc.get('Id'),
                        'soort': doc_type,
                        'categorie': category,
                        'type': doc_type_field,
                        'onderwerp': doc.get('Onderwerp', '')[:100] if doc.get('Onderwerp') else '',
                        'nummer': doc.get('Nummer'),
                        'datum': doc.get('Datum')
                    })

        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            continue

    # Print results
    print(f"\n=== DOCUMENT ANALYSIS RESULTS ===")
    print(f"Total documents analyzed: {total_docs:,}")
    print(f"Document files processed: {len(doc_files)}")

    print(f"\n=== DOCUMENT SOORTEN (Types) ===")
    for soort, count in sorted(doc_soorten.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_docs) * 100
        print("25")

    print(f"\n=== DOCUMENT CATEGORIEEN (Categories) ===")
    for cat, count in sorted(doc_categories.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_docs) * 100
        print("25")

    print(f"\n=== DOCUMENT TYPES ===")
    for dtype, count in sorted(doc_types.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_docs) * 100
        print("25")

    # Look for law-related documents
    law_related = []
    for soort in doc_soorten:
        if any(keyword in soort.lower() for keyword in ['wet', 'wets', 'wetten', 'artikel', 'artikel', 'bepaling']):
            law_related.append((soort, doc_soorten[soort]))

    if law_related:
        print(f"\n=== POTENTIAL LAW-RELATED DOCUMENTS ===")
        for soort, count in law_related:
            print(f"- {soort}: {count:,} documents")
    else:
        print(f"\n=== NO LAW-RELATED DOCUMENTS FOUND IN DOCUMENT ENTITY ===")

    # Show sample documents
    print(f"\n=== SAMPLE DOCUMENTS (first 10) ===")
    for i, doc in enumerate(sample_docs, 1):
        print(f"\nDocument {i}:")
        print(f"  ID: {doc['id']}")
        print(f"  Soort: {doc['soort']}")
        print(f"  Categorie: {doc['categorie']}")
        print(f"  Type: {doc['type']}")
        print(f"  Nummer: {doc['nummer']}")
        print(f"  Datum: {doc['datum']}")
        print(f"  Onderwerp: {doc['onderwerp'][:100]}...")

if __name__ == "__main__":
    analyze_all_documents()