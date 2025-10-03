#!/usr/bin/env python3
"""
Check document entity for laws and amendments
"""

import json
from pathlib import Path
from collections import Counter

def analyze_document_types():
    """Analyze document types to find laws and amendments"""

    doc_dir = Path('bronmateriaal-onbewerkt/document')

    if not doc_dir.exists():
        print("❌ Document directory not found")
        return

    # Load first few document files
    doc_files = list(doc_dir.glob('*fullterm*.json'))[:3]  # First 3 files
    print(f"📁 Analyzing first {len(doc_files)} document files")

    all_docs = []
    for file_path in doc_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list):
                all_docs.extend(data)
        except Exception as e:
            print(f"❌ Error loading {file_path}: {e}")

    print(f"✅ Sample documents loaded: {len(all_docs)}")

    # Analyze document types
    soorten = Counter()
    for doc in all_docs:
        soort = doc.get('Soort', 'Unknown')
        soorten[soort] += 1

    print("\n📄 DOCUMENT TYPES (sample):")
    print("=" * 35)

    total_count = sum(soorten.values())
    for soort, count in sorted(soorten.items(), key=lambda x: x[1], reverse=True)[:20]:
        percentage = (count / total_count) * 100
        print("15")

    # Check for law-related documents
    print("\n🎯 LAW-RELATED DOCUMENT TYPES:")
    law_types = ['Wet', 'Wetsvoorstel', 'Wetsartikel', 'Amendement', 'Wijzigingsvoorstel']
    for law_type in law_types:
        count = soorten.get(law_type, 0)
        if count > 0:
            percentage = (count / total_count) * 100
            print("15")

    # Show sample law documents
    print("\n📋 SAMPLE LAW DOCUMENTS:")
    print("=" * 25)

    law_samples = {}
    for doc in all_docs[:200]:  # Check first 200
        soort = doc.get('Soort', 'Unknown')
        if soort in law_types and soort not in law_samples:
            law_samples[soort] = doc
            if len(law_samples) >= len(law_types):
                break

    for soort, doc in law_samples.items():
        titel = doc.get('Titel', '')[:60]
        print(f"{soort}: {titel}...")

if __name__ == "__main__":
    analyze_document_types()