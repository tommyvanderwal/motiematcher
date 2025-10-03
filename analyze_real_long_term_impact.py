#!/usr/bin/env python3
"""
Script om echte parlementaire data te combineren en te analyseren op lange termijn impact.
Focus op democratie, vrijheid van meningsuiting en 10+ jaar impact.
"""

import json
import random
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

def load_real_zaak_data():
    """Laad alle echte zaak data (moties, wetten, amendementen)"""
    zaken = []
    zaak_path = Path("bronmateriaal-onbewerkt/zaak")

    # Zoek naar alle zaak_page en moties_page bestanden
    patterns = ["zaak_page_*_fullterm_*.json", "moties_page_*_*.json"]

    for pattern in patterns:
        for file_path in zaak_path.glob(pattern):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    page_data = json.load(f)
                    if isinstance(page_data, list):
                        zaken.extend([z for z in page_data if z is not None])
                    else:
                        zaken.extend([z for z in page_data.get('value', []) if z is not None])
                print(f"Geladen: {file_path.name} - {len(page_data) if isinstance(page_data, list) else len(page_data.get('value', []))} items")
            except Exception as e:
                print(f"Fout bij laden {file_path}: {e}")
                continue

    return zaken

def load_real_stemming_data():
    """Laad alle echte stemming data"""
    stemmingen = []
    stemming_path = Path("bronmateriaal-onbewerkt/stemming")

    for file_path in stemming_path.glob("*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                page_data = json.load(f)
                if isinstance(page_data, list):
                    stemmingen.extend(page_data)
                else:
                    stemmingen.extend(page_data.get('value', []))
            print(f"Geladen: {file_path.name} - {len(page_data) if isinstance(page_data, list) else len(page_data.get('value', []))} stemmingen")
        except Exception as e:
            print(f"Fout bij laden {file_path}: {e}")
            continue

    return stemmingen

def enrich_zaken_with_voting(zaken, stemmingen):
    """Combineer zaken met stemming data"""
    zaak_stemmingen = defaultdict(list)

    # Koppel stemmingen aan zaken via Besluit_Id
    for stemming in stemmingen:
        besluit_id = stemming.get('Besluit_Id')
        if besluit_id:
            zaak_stemmingen[besluit_id].append(stemming)

    enriched_zaken = []
    for zaak in zaken:
        zaak_id = zaak.get('Id')
        enriched_zaak = zaak.copy()

        if zaak_id in zaak_stemmingen:
            enriched_zaak['voting_records'] = zaak_stemmingen[zaak_id]
        else:
            enriched_zaak['voting_records'] = []

        enriched_zaken.append(enriched_zaak)

    return enriched_zaken

def analyze_long_term_impact(zaak):
    """Beoordeel of zaak lange termijn impact heeft (10+ jaar)"""
    titel = zaak.get('Titel')
    onderwerp = zaak.get('Onderwerp')
    soort = zaak.get('Soort')
    
    # Handle None values safely
    titel = titel.lower() if isinstance(titel, str) else ''
    onderwerp = onderwerp.lower() if isinstance(onderwerp, str) else ''
    soort = soort.lower() if isinstance(soort, str) else ''

    # Keywords voor lange termijn impact
    high_impact_keywords = {
        'democratie_fundamenteel': [
            'grondwet', 'constitutie', 'referendum', 'volksvertegenwoordiging',
            'parlement', 'kamer', 'eerste kamer', 'tweede kamer',
            'staatsinrichting', 'democratische beginselen'
        ],
        'vrijheid_meningsuiting': [
            'vrijheid van meningsuiting', 'persvrijheid', 'uitingsvrijheid',
            'journalist', 'media', 'censuur', 'propaganda',
            'woordvrijheid', 'drukpers', 'publicatie'
        ],
        'eu_na_influence': [
            'europa', 'eu ', 'european union', 'navo', 'nato',
            'soevereiniteit', 'nationale onafhankelijkheid',
            'eu-lidmaatschap', 'eu-verdrag', 'eu-wetgeving'
        ],
        'monetair_systeem': [
            'euro', 'ecb', 'europese centrale bank', 'geld',
            'monetair beleid', 'valuta', 'digitale euro', 'cbdc',
            'bankwezen', 'financieel systeem'
        ],
        'belasting_fiscale': [
            'belasting', 'btw', 'fiscale', 'heffing', 'inkomstenbelasting',
            'vennootschapsbelasting', 'erfbelasting', 'schenkingsrecht'
        ],
        'sociale_zekerheid_lang': [
            'pensioen', 'aow', 'bijstand', 'bijstandsuitkering',
            'sociale verzekering', 'zorgstelsel', 'gezondheidszorg'
        ],
        'onderwijs_hoger': [
            'universiteit', 'hoger onderwijs', 'wetenschap',
            'onderzoek', 'innovatie', 'technologie'
        ],
        'veiligheid_nationaal': [
            'veiligheid', 'inlichtingendienst', 'aivd', 'mivd',
            'terrorisme', 'extremisme', 'staatsveiligheid'
        ]
    }

    impact_score = 0
    matched_categories = []

    # Controleer titel en onderwerp
    text_to_check = titel + ' ' + onderwerp

    for category, keywords in high_impact_keywords.items():
        if any(keyword in text_to_check for keyword in keywords):
            matched_categories.append(category)
            # Gewicht per categorie
            if category in ['democratie_fundamenteel', 'vrijheid_meningsuiting']:
                impact_score += 10  # Hoogste gewicht
            elif category in ['eu_na_influence', 'monetair_systeem']:
                impact_score += 8   # Zeer hoog gewicht
            else:
                impact_score += 6   # Hoog gewicht

    # Extra gewicht voor bepaalde soorten
    if soort == 'wet':
        impact_score += 3  # Wetten hebben meer impact dan moties
    elif soort == 'amendement':
        impact_score += 2

    # Minimum score voor lange termijn impact
    has_long_term_impact = impact_score >= 8

    return {
        'has_long_term_impact': has_long_term_impact,
        'impact_score': impact_score,
        'categories': matched_categories,
        'reasoning': f"Impact score: {impact_score}, Categories: {matched_categories}"
    }

def select_high_impact_items(enriched_zaken, max_items=50):
    """Selecteer eerste 50 items met lange termijn impact"""
    analyzed_items = []
    
    print(f"Debug: Processing first {min(max_items, len(enriched_zaken))} enriched_zaken")
    
    for i, zaak in enumerate(enriched_zaken[:max_items]):  # Neem eerste 50
        print(f"Debug: zaak {i} type: {type(zaak)}, is None: {zaak is None}")
        if zaak is None:  # Skip None zaken
            print(f"Debug: Skipping None zaak at index {i}")
            continue

        try:
            impact_analysis = analyze_long_term_impact(zaak)
            if impact_analysis['has_long_term_impact']:
                analyzed_items.append({
                    'zaak': zaak,
                    'impact_analysis': impact_analysis
                })
        except Exception as e:
            print(f"Debug: Error analyzing zaak {i}: {e}")
            continue

    # Sorteer op impact score (hoogste eerst)
    analyzed_items.sort(key=lambda x: x['impact_analysis']['impact_score'], reverse=True)

    return analyzed_items

def create_enriched_output(analyzed_items):
    """Maak nette output voor website"""
    output = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'total_analyzed': len(analyzed_items),
            'data_source': 'real_parliamentary_data',
            'analysis_focus': 'long_term_democratic_impact_10_years',
            'priority_categories': [
                'democratie_fundamenteel',
                'vrijheid_meningsuiting',
                'eu_na_influence',
                'monetair_systeem'
            ]
        },
        'selected_items': []
    }

    for item in analyzed_items:
        zaak = item['zaak']
        analysis = item['impact_analysis']

        enriched_item = {
            'id': zaak.get('Id'),
            'type': zaak.get('Soort'),
            'title': zaak.get('Titel', ''),
            'subject': zaak.get('Onderwerp', ''),
            'date': zaak.get('GestartOp', ''),
            'status': zaak.get('Status', ''),
            'long_term_impact': analysis['has_long_term_impact'],
            'impact_score': analysis['impact_score'],
            'impact_categories': analysis['categories'],
            'voting_records': zaak.get('voting_records', []),
            'analysis_reasoning': analysis['reasoning']
        }

        output['selected_items'].append(enriched_item)

    return output

def main():
    print("Laden echte parlementaire zaak data...")
    zaken = load_real_zaak_data()
    print(f"Totaal zaken geladen: {len(zaken)}")

    print("\nLaden echte stemming data...")
    stemmingen = load_real_stemming_data()
    print(f"Totaal stemmingen geladen: {len(stemmingen)}")

    print("\nCombineren zaken met stemming data...")
    enriched_zaken = enrich_zaken_with_voting(zaken, stemmingen)
    zaken_met_stemmingen = [z for z in enriched_zaken if z.get('voting_records')]
    print(f"Zaken met stemming data: {len(zaken_met_stemmingen)}")

    print("\nAnalyseren lange termijn impact (eerste 50 items)...")
    high_impact_items = select_high_impact_items(enriched_zaken, max_items=50)
    print(f"Items met lange termijn impact: {len(high_impact_items)}")

    print("\nMaken van output...")
    output = create_enriched_output(high_impact_items)

    # Save results
    output_file = 'real_high_impact_parliamentary_items.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Resultaten opgeslagen in {output_file}")

    # Print summary
    print("\nSAMENVATTING:")
    print(f"Totaal geanalyseerd: {len(high_impact_items)}")
    print(f"Gemiddelde impact score: {sum(item['impact_analysis']['impact_score'] for item in high_impact_items) / len(high_impact_items) if high_impact_items else 0:.1f}")

    category_counts = Counter()
    for item in high_impact_items:
        for cat in item['impact_analysis']['categories']:
            category_counts[cat] += 1

    print(f"Top categorieën: {dict(category_counts.most_common(5))}")

    # Toon top 5 items
    print("\nTOP 5 ITEMS MET HOOGSTE IMPACT:")
    for i, item in enumerate(high_impact_items[:5], 1):
        zaak = item['zaak']
        analysis = item['impact_analysis']
        title = zaak.get('Titel', '') or ''
        print(f"{i}. {title[:60]}...")
        print(f"   Score: {analysis['impact_score']}, Categories: {analysis['categories']}")

if __name__ == '__main__':
    main()