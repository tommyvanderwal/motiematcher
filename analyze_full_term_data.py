#!/usr/bin/env python3
"""
Data Quality Analysis for Full Term Collection
Onderzoek naar errors, datum distributie, en data kwaliteit
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict, Counter
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FullTermDataAnalyzer:
    def __init__(self, base_dir="bronmateriaal-onbewerkt"):
        self.base_dir = Path(base_dir)

    def load_entity_data(self, entity_type, pattern="*fullterm*.json"):
        """Laad alle data voor een entity type"""
        entity_dir = self.base_dir / entity_type.lower()
        all_data = []

        if not entity_dir.exists():
            logger.warning(f"Directory {entity_dir} does not exist")
            return all_data

        for file in entity_dir.glob(pattern):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_data.extend(data)
                    else:
                        all_data.append(data)
            except Exception as e:
                logger.error(f"Error loading {file}: {e}")

        return all_data

    def analyze_collection_completeness(self):
        """Analyseer of de collectie compleet is"""
        logger.info("🔍 ANALYZING COLLECTION COMPLETENESS")
        logger.info("=" * 50)

        entities = ['zaak', 'stemming', 'besluit', 'document', 'activiteit', 'persoon', 'fractie', 'vergadering', 'agendapunt']

        for entity in entities:
            data = self.load_entity_data(entity)
            logger.info(f"{entity:12}: {len(data):6,} records")

            # Check voor lege files of incomplete data
            if len(data) == 0:
                logger.warning(f"❌ {entity}: NO DATA COLLECTED!")
            elif len(data) < 100:
                logger.warning(f"⚠️  {entity}: Only {len(data)} records - might be incomplete")

    def analyze_date_distribution(self):
        """Analyseer GewijzigdOp datum distributie"""
        logger.info("\n📅 ANALYZING DATE DISTRIBUTION")
        logger.info("=" * 50)

        entities = ['zaak', 'stemming', 'besluit', 'document', 'activiteit', 'vergadering', 'agendapunt']

        cutoff_date = datetime(2023, 12, 6)

        for entity in entities:
            data = self.load_entity_data(entity)
            if not data:
                continue

            logger.info(f"\n{entity.upper()} Date Analysis:")
            logger.info("-" * 30)

            date_counts = defaultdict(int)
            old_records = []
            future_records = []

            for record in data:
                date_str = record.get('GewijzigdOp', '')
                if date_str:
                    try:
                        # Handle different date formats
                        if date_str.endswith('Z'):
                            date_str = date_str[:-1] + '+00:00'
                        record_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))

                        date_key = record_date.strftime('%Y-%m-%d')
                        date_counts[date_key] += 1

                        if record_date.replace(tzinfo=None) < cutoff_date:
                            old_records.append((record_date, record))
                        elif record_date > datetime.now():
                            future_records.append((record_date, record))

                    except Exception as e:
                        logger.warning(f"Could not parse date '{date_str}': {e}")

            # Show top dates with most records
            if date_counts:
                sorted_dates = sorted(date_counts.items(), key=lambda x: x[1], reverse=True)
                logger.info("Top 10 dates with most records:")
                for date, count in sorted_dates[:10]:
                    logger.info(f"  {date}: {count} records")

            # Check for old/future records
            if old_records:
                logger.warning(f"❌ Found {len(old_records)} records older than Dec 6, 2023!")
                # Show some examples
                for date, record in old_records[:3]:
                    logger.warning(f"   Old record: {date.strftime('%Y-%m-%d')} - {record.get('Nummer', record.get('Id', 'Unknown'))}")

            if future_records:
                logger.warning(f"⚠️  Found {len(future_records)} records with future dates!")
                for date, record in future_records[:3]:
                    logger.warning(f"   Future record: {date.strftime('%Y-%m-%d')} - {record.get('Nummer', record.get('Id', 'Unknown'))}")

    def analyze_persoon_changes(self):
        """Analyseer veranderingen in parlementariërs"""
        logger.info("\n👥 ANALYZING PERSOON CHANGES")
        logger.info("=" * 50)

        personen = self.load_entity_data('persoon')
        logger.info(f"Total personen: {len(personen)}")

        # Analyseer status veranderingen
        status_counts = Counter()
        functie_start_dates = []
        functie_eind_dates = []

        for persoon in personen:
            status = persoon.get('Status', 'Unknown')
            status_counts[status] += 1

            # Check functie periodes
            functies = persoon.get('Functie', [])
            if not isinstance(functies, list):
                functies = [functies] if functies else []
            
            for functie in functies:
                if isinstance(functie, str):
                    # Skip string functies for now
                    continue
                    
                start_date = functie.get('FunctieStart')
                eind_date = functie.get('FunctieEind')

                if start_date:
                    try:
                        start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                        functie_start_dates.append(start_dt)
                    except:
                        pass

                if eind_date:
                    try:
                        eind_dt = datetime.fromisoformat(eind_date.replace('Z', '+00:00'))
                        functie_eind_dates.append(eind_dt)
                    except:
                        pass

        logger.info("Persoon status distribution:")
        for status, count in status_counts.most_common():
            logger.info(f"  {status}: {count}")

        # Analyseer functie veranderingen sinds 2023
        cutoff = datetime(2023, 12, 6)
        recent_starts = [d for d in functie_start_dates if d >= cutoff]
        recent_ends = [d for d in functie_eind_dates if d >= cutoff]

        logger.info(f"\nFunctie changes since Dec 2023:")
        logger.info(f"  New functies: {len(recent_starts)}")
        logger.info(f"  Ended functies: {len(recent_ends)}")

        if recent_ends:
            logger.info("  Kamerleden die vertrokken sinds Dec 2023:")
            # Group by month
            end_months = Counter(d.strftime('%Y-%m') for d in recent_ends)
            for month, count in sorted(end_months.items()):
                logger.info(f"    {month}: {count} vertrekken")

    def check_api_errors(self):
        """Check voor API errors tijdens collectie"""
        logger.info("\n🚨 CHECKING FOR API ERRORS")
        logger.info("=" * 50)

        # Check besluit collection specifically for the 500 error
        besluit_data = self.load_entity_data('besluit')
        logger.info(f"Besluit records collected: {len(besluit_data)}")

        # Check if we have gaps in the data
        if besluit_data:
            # Sort by some field to check continuity
            sorted_besluiten = sorted(besluit_data, key=lambda x: x.get('GewijzigdOp', ''), reverse=True)
            logger.info(f"Newest besluit: {sorted_besluiten[0].get('GewijzigdOp', 'Unknown')}")
            logger.info(f"Oldest besluit: {sorted_besluiten[-1].get('GewijzigdOp', 'Unknown')}")

            # Check for date gaps that might indicate missing data due to the 500 error
            dates = []
            for besluit in besluit_data[:100]:  # Check first 100
                date_str = besluit.get('GewijzigdOp', '')
                if date_str:
                    try:
                        date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        dates.append(date)
                    except:
                        pass

            if dates:
                dates.sort(reverse=True)
                logger.info("Date range check (newest 100):")
                logger.info(f"  From: {dates[0].strftime('%Y-%m-%d %H:%M')}")
                logger.info(f"  To: {dates[-1].strftime('%Y-%m-%d %H:%M')}")

    def analyze_old_zaken_in_collection(self):
        """Analyseer zaken uit de vorige kamerperiode (voor 6 dec 2023)"""
        logger.info("\n📜 ANALYZING PREVIOUS TERM ZAKEN IN COLLECTION")
        logger.info("=" * 50)

        zaken = self.load_entity_data('zaak')
        cutoff_date = datetime(2023, 12, 6)

        old_zaken = []
        for zaak in zaken:
            date_str = zaak.get('GewijzigdOp', '')
            if date_str:
                try:
                    zaak_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    if zaak_date.replace(tzinfo=None) < cutoff_date:
                        old_zaken.append((zaak_date, zaak))
                except:
                    pass

        logger.info(f"Found {len(old_zaken)} zaken from previous term (before Dec 6, 2023)")

        if old_zaken:
            # Sort by age
            old_zaken.sort(key=lambda x: x[0])

            logger.info("\nOldest zaken in collection (previous term):")
            for date, zaak in old_zaken[:5]:
                logger.info(f"  {date.strftime('%Y-%m-%d')}: {zaak.get('Nummer', 'Unknown')} - {zaak.get('Titel', '')[:60]}...")

            # Group by year
            year_counts = Counter(date.year for date, _ in old_zaken)
            logger.info("\nPrevious term zaken by year:")
            for year, count in sorted(year_counts.items()):
                logger.info(f"  {year}: {count} zaken")
        else:
            logger.info("✅ No previous term zaken found - date filtering working correctly")

    def run_full_analysis(self):
        """Voer complete analyse uit"""
        logger.info("🏛️ FULL TERM DATA QUALITY ANALYSIS")
        logger.info("=" * 60)

        self.analyze_collection_completeness()
        self.analyze_date_distribution()
        self.analyze_persoon_changes()
        self.check_api_errors()
        self.analyze_old_zaken_in_collection()

        logger.info("\n✅ ANALYSIS COMPLETE")
        logger.info("Review the findings above for data quality issues")

if __name__ == "__main__":
    analyzer = FullTermDataAnalyzer()
    analyzer.run_full_analysis()