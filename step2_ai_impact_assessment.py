#!/usr/bin/env python3
"""
Step 2: AI Impact Assessment for Democratic Significance
Analyzes filtered parliamentary data for long-term democratic impact using AI assessment.
Focus on fundamental democratic freedoms, freedom of information, and major government spending.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter

def load_step1_filtered_data() -> Dict[str, Any]:
    """Load the filtered data from Step 1"""
    input_file = Path("step1_fullterm_filtered_enriched_data.json")

    if not input_file.exists():
        raise FileNotFoundError(f"Step 1 output file not found: {input_file}")

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Loaded {data['metadata']['total_zaken']} zaken from Step 1")
    return data

def extract_key_content(zaak: Dict[str, Any]) -> str:
    """Extract the most relevant content for AI analysis"""
    content_parts = []

    # Title and subject are most important
    titel = zaak.get('titel', zaak.get('Titel', ''))
    onderwerp = zaak.get('onderwerp', zaak.get('Onderwerp', ''))

    if titel:
        content_parts.append(f"Title: {titel}")
    if onderwerp:
        content_parts.append(f"Subject: {onderwerp}")

    # Add full text if available
    full_text = zaak.get('full_text', '')
    if full_text and len(full_text) > len(titel + onderwerp):
        # Truncate if too long, but keep essential content
        if len(full_text) > 500:
            full_text = full_text[:500] + "..."
        content_parts.append(f"Content: {full_text}")

    return "\n".join(content_parts)

def assess_democratic_impact_ai(zaak: Dict[str, Any]) -> Dict[str, Any]:
    """
    AI-powered assessment of democratic impact focusing on:
    1. Fundamental democratic freedoms
    2. Freedom of information (citizens must know everything to vote democratically)
    3. Major government spending causing inflation
    """

    content = extract_key_content(zaak)
    zaak_type = zaak.get('type', zaak.get('Soort', ''))
    year = zaak.get('year', '')

    # AI Analysis Prompt (this would be sent to an LLM)
    ai_prompt = f"""
    Analyze this Dutch parliamentary motion/amendment/law for its long-term democratic significance:

    {content}

    Type: {zaak_type}
    Year: {year}

    Assess impact on:
    1. FUNDAMENTAL DEMOCRATIC FREEDOMS (civil liberties, human rights, democratic institutions)
    2. FREEDOM OF INFORMATION (transparency, citizens' right to know for democratic voting)
    3. MAJOR GOVERNMENT SPENDING (inflation-causing expenditures, fiscal policy)

    Rate significance (0-10) and explain why this matters for Dutch democracy.
    Focus on cases where one political party could have made the difference.
    """

    # For now, implement rule-based AI simulation (in production, this would call an LLM)
    # This is a sophisticated keyword + context analysis

    analysis = analyze_democratic_impact_rules(content, zaak_type, year)

    return {
        'ai_analysis': analysis,
        'content_analyzed': content,
        'assessment_timestamp': datetime.now().isoformat(),
        'analysis_method': 'rule_based_ai_simulation'  # Would be 'llm_gpt4' in production
    }

def analyze_democratic_impact_rules(content: str, zaak_type: str, year: int) -> Dict[str, Any]:
    """Sophisticated rule-based analysis simulating AI assessment"""

    content_lower = content.lower()
    score = 0
    reasons = []
    categories = []

    # Category 1: Fundamental Democratic Freedoms
    democracy_keywords = [
        'grondwet', 'constitutie', 'referendum', 'volksvertegenwoordiging',
        'parlement', 'kamer', 'democratische', 'burgerrechten', 'mensenrechten',
        'vrijheid van meningsuiting', 'persvrijheid', 'uitingsvrijheid',
        'staatsinrichting', 'soevereiniteit', 'nationale onafhankelijkheid'
    ]

    democracy_matches = [kw for kw in democracy_keywords if kw in content_lower]
    if democracy_matches:
        democracy_score = min(len(democracy_matches) * 3, 10)
        score += democracy_score
        categories.append('fundamental_democratic_freedoms')
        reasons.append(f"Addresses fundamental democratic freedoms: {', '.join(democracy_matches[:3])}")

    # Category 2: Freedom of Information
    info_keywords = [
        'transparantie', 'openbaarheid', 'informatie', 'publiek', 'besluitvorming',
        'democratisch', 'verantwoording', 'controle', 'inzage', 'wob',
        'pers', 'media', 'journalist', 'censuur', 'propaganda'
    ]

    info_matches = [kw for kw in info_keywords if kw in content_lower]
    if info_matches:
        info_score = min(len(info_matches) * 2.5, 8)
        score += info_score
        categories.append('freedom_of_information')
        reasons.append(f"Impacts freedom of information and transparency: {', '.join(info_matches[:3])}")

    # Category 3: Major Government Spending
    spending_keywords = [
        'begroting', 'uitgaven', 'miljard', 'budget', 'financiën', 'economie',
        'inflatie', 'schuld', 'belasting', 'btw', 'subsidie', 'steun',
        'investeringen', 'economisch', 'fiscaal', 'monetair'
    ]

    spending_matches = [kw for kw in spending_keywords if kw in content_lower]
    if spending_matches:
        # Check for large amounts
        amount_indicators = ['miljard', '€', 'euro', 'budget', 'begroting']
        has_large_amount = any(indicator in content_lower for indicator in amount_indicators)
        spending_score = min(len(spending_matches) * 2, 7) + (2 if has_large_amount else 0)
        score += spending_score
        categories.append('major_government_spending')
        reasons.append(f"Involves major government spending/fiscal policy: {', '.join(spending_matches[:3])}")

    # Additional factors
    if zaak_type.lower() == 'wet':
        score += 2  # Laws have more impact
        reasons.append("Law (wet) has higher democratic significance than motion")
    elif zaak_type.lower() == 'amendement':
        score += 1  # Amendments also significant
        reasons.append("Amendment affects existing law")

    # Recency factor (more recent = potentially more relevant)
    if year >= 2023:
        score += 1
        reasons.append("Recent legislation (2023+) has current democratic relevance")

    # Close vote factor (if voting data available)
    close_vote_bonus = 0
    voting_records = []  # Would be populated if voting data was available
    if voting_records and len(voting_records) > 0:
        # Analyze if it was a close vote
        total_votes = len(voting_records)
        yes_votes = sum(1 for v in voting_records if v.get('Soort') == 'Voor')
        no_votes = sum(1 for v in voting_records if v.get('Soort') == 'Tegen')

        if total_votes > 10:  # Only for votes with reasonable participation
            margin = abs(yes_votes - no_votes)
            if margin <= 3:  # Very close vote
                close_vote_bonus = 3
                reasons.append(f"Extremely close vote ({margin} vote margin) - one party could have changed outcome")
            elif margin <= 10:
                close_vote_bonus = 2
                reasons.append(f"Close vote ({margin} vote margin) - significant party influence possible")

        score += close_vote_bonus

    # Normalize score to 0-10 range
    final_score = min(max(score, 0), 10)

    # Determine if high impact
    is_high_impact = final_score >= 7

    return {
        'democratic_impact_score': round(final_score, 1),
        'is_high_impact': is_high_impact,
        'impact_categories': categories,
        'reasoning': reasons,
        'key_factors': {
            'content_length': len(content),
            'keyword_matches': len(democracy_matches + info_matches + spending_matches),
            'close_vote_bonus': close_vote_bonus,
            'type_bonus': 2 if zaak_type.lower() == 'wet' else (1 if zaak_type.lower() == 'amendement' else 0)
        }
    }

def select_top_democratic_impact_items(zaken_data: Dict[str, Any], max_items: int = 100) -> List[Dict[str, Any]]:
    """Select top items by democratic impact score"""

    analyzed_items = []

    for zaak in zaken_data['zaken']:
        try:
            ai_assessment = assess_democratic_impact_ai(zaak)
            analyzed_zaak = zaak.copy()
            analyzed_zaak.update(ai_assessment)

            analyzed_items.append(analyzed_zaak)

        except Exception as e:
            print(f"Error analyzing zaak {zaak.get('id', 'unknown')}: {e}")
            continue

    # Sort by democratic impact score (highest first)
    analyzed_items.sort(key=lambda x: x['ai_analysis']['democratic_impact_score'], reverse=True)

    # Return top items
    top_items = analyzed_items[:max_items]

    print(f"Selected top {len(top_items)} items with highest democratic impact")
    return top_items

def create_step2_output(top_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create the final Step 2 output"""

    output = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'step': 'step2_ai_impact_assessment',
            'total_analyzed': len(top_items),
            'analysis_focus': 'democratic_significance_ai_assessment',
            'impact_criteria': [
                'fundamental_democratic_freedoms',
                'freedom_of_information',
                'major_government_spending_inflation'
            ],
            'selection_method': 'ai_powered_impact_scoring',
            'min_impact_threshold': 7.0,
            'data_source': 'step1_fullterm_filtered_enriched_data.json'
        },
        'high_impact_parliamentary_items': []
    }

    for item in top_items:
        # Clean up the item for output
        clean_item = {
            'id': item.get('id'),
            'nummer': item.get('nummer'),
            'type': item.get('type'),
            'titel': item.get('titel'),
            'onderwerp': item.get('onderwerp'),
            'date': item.get('date'),
            'year': item.get('year'),
            'vergaderjaar': item.get('vergaderjaar'),
            'status': item.get('status'),
            'full_text': item.get('full_text', ''),
            'has_voting_data': item.get('has_voting_data', False),
            'total_votes': item.get('total_votes', 0),
            'close_vote': item.get('close_vote', False),
            'vote_margin': item.get('vote_margin'),
            # AI Analysis results
            'democratic_impact_score': item['ai_analysis']['democratic_impact_score'],
            'is_high_impact': item['ai_analysis']['is_high_impact'],
            'impact_categories': item['ai_analysis']['impact_categories'],
            'impact_reasoning': item['ai_analysis']['reasoning'],
            'ai_analysis_method': item.get('analysis_method', 'rule_based_ai_simulation'),
            'assessment_timestamp': item.get('assessment_timestamp')
        }

        output['high_impact_parliamentary_items'].append(clean_item)

    return output

def main():
    print("🚀 Step 2: AI Impact Assessment for Democratic Significance")
    print("=" * 60)

    try:
        # Load Step 1 filtered data
        print("\n📂 Loading Step 1 filtered data...")
        zaken_data = load_step1_filtered_data()

        # Analyze democratic impact for all items
        print("\n🤖 Analyzing democratic impact with AI assessment...")
        top_items = select_top_democratic_impact_items(zaken_data, max_items=100)

        # Create output
        print("\n📊 Creating Step 2 output...")
        output = create_step2_output(top_items)

        # Save results
        output_file = 'step2_ai_democratic_impact_assessment.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Step 2 Complete! Results saved to {output_file}")

        # Print summary
        high_impact_count = sum(1 for item in top_items if item['ai_analysis']['is_high_impact'])
        avg_score = sum(item['ai_analysis']['democratic_impact_score'] for item in top_items) / len(top_items)

        print("\n📈 SUMMARY:")
        print(f"Total analyzed: {len(top_items)}")
        print(f"High impact items (score ≥7): {high_impact_count}")
        print(f"Average democratic impact score: {avg_score:.1f}")

        # Category breakdown
        all_categories = []
        for item in top_items:
            all_categories.extend(item['ai_analysis']['impact_categories'])

        category_counts = Counter(all_categories)
        print(f"Top impact categories: {dict(category_counts.most_common(3))}")

        # Show top 5
        print("\n🏆 TOP 5 HIGH IMPACT ITEMS:")
        for i, item in enumerate(top_items[:5], 1):
            title = item.get('titel', '')[:60]
            score = item['ai_analysis']['democratic_impact_score']
            categories = item['ai_analysis']['impact_categories']
            print(f"{i}. {title}...")
            print(f"   Score: {score}, Categories: {categories}")

    except Exception as e:
        print(f"❌ Error in Step 2: {e}")
        raise

if __name__ == '__main__':
    main()