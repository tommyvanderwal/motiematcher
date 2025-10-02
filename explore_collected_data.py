#!/usr/bin/env python3
"""
Data Explorer voor verzamelde parlementaire data
Verkent de bronmateriaal-onbewerkt directory en toont voorbeelden van verzamelde moties en stemmingen
"""

import json
import os
from datetime import datetime
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataExplorer:
    def __init__(self, data_dir="bronmateriaal-onbewerkt"):
        self.data_dir = Path(data_dir)
        
    def get_directory_stats(self):
        """Toon overzicht van verzamelde data"""
        logger.info("📊 Data overzicht:")
        
        total_size = 0
        total_files = 0
        
        for subdir in ['zaak', 'stemming', 'besluit', 'agendapunt', 'document', 'activiteit']:
            subdir_path = self.data_dir / subdir
            if subdir_path.exists():
                files = list(subdir_path.glob('*.json'))
                size = sum(f.stat().st_size for f in files)
                total_size += size
                total_files += len(files)
                
                logger.info(f"  {subdir:12}: {len(files):3d} files, {size/1024/1024:.1f} MB")
        
        logger.info(f"  {'TOTAAL':12}: {total_files:3d} files, {total_size/1024/1024:.1f} MB")
        return total_files, total_size
        
    def explore_motie_data(self):
        """Verken motie data uit zaak directory"""
        logger.info("\n📝 Motie data verkenning:")
        
        zaak_dir = self.data_dir / 'zaak'
        if not zaak_dir.exists():
            logger.warning("Geen zaak directory gevonden!")
            return
            
        motie_files = list(zaak_dir.glob('moties_page_*.json'))
        logger.info(f"Gevonden {len(motie_files)} motie bestanden")
        
        if not motie_files:
            return
            
        # Bekijk eerste bestand
        first_file = motie_files[0]
        logger.info(f"Verkennen: {first_file.name}")
        
        try:
            with open(first_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if 'value' in data and len(data['value']) > 0:
                total_moties = len(data['value'])
                logger.info(f"  Moties in dit bestand: {total_moties}")
                
                # Toon eerste motie als voorbeeld
                sample_motie = data['value'][0]
                logger.info(f"  Voorbeeld motie eigenschappen:")
                for key in sorted(sample_motie.keys()):
                    value = sample_motie[key]
                    if isinstance(value, str) and len(value) > 100:
                        value = value[:100] + "..."
                    logger.info(f"    {key:20}: {value}")
                    
                # Zoek naar interessante moties
                logger.info(f"\n  🔍 Interessante moties uit dit bestand:")
                for i, motie in enumerate(data['value'][:5]):  # Eerste 5
                    onderwerp = motie.get('Onderwerp', 'Geen onderwerp')
                    titel = motie.get('TitelKort', motie.get('TitelLang', 'Geen titel'))
                    indiener = motie.get('IndienerNaam', 'Onbekend')
                    
                    if onderwerp or titel != 'Geen titel':
                        logger.info(f"    {i+1}. {titel[:80]}...")
                        logger.info(f"       Onderwerp: {onderwerp}")
                        logger.info(f"       Indiener: {indiener}")
                        
        except Exception as e:
            logger.error(f"Fout bij lezen motie data: {e}")
            
    def explore_voting_data(self):
        """Verken stemming data"""
        logger.info("\n🗳️ Stemming data verkenning:")
        
        stemming_dir = self.data_dir / 'stemming'
        if not stemming_dir.exists():
            logger.warning("Geen stemming directory gevonden!")
            return
            
        voting_files = list(stemming_dir.glob('votes_page_*.json'))
        logger.info(f"Gevonden {len(voting_files)} stemming bestanden")
        
        if not voting_files:
            return
            
        # Analyse laatste bestand (meest recente data)
        last_file = sorted(voting_files)[-1]
        logger.info(f"Verkennen: {last_file.name}")
        
        try:
            with open(last_file, 'r', encoding='utf-8') as f:
                votes = json.load(f)
                
            logger.info(f"  Stemmingen in dit bestand: {len(votes)}")
            
            if len(votes) > 0:
                # Analyse partijen
                parties = {}
                decisions = set()
                
                for vote in votes:
                    party = vote.get('FractieNaam', 'Onbekend')
                    decision_id = vote.get('Besluit_Id')
                    vote_type = vote.get('Soort', 'Onbekend')
                    
                    if party not in parties:
                        parties[party] = {'voor': 0, 'tegen': 0, 'onthouding': 0}
                    
                    if vote_type.lower() == 'voor':
                        parties[party]['voor'] += 1
                    elif vote_type.lower() == 'tegen':
                        parties[party]['tegen'] += 1
                    else:
                        parties[party]['onthouding'] += 1
                        
                    if decision_id:
                        decisions.add(decision_id)
                
                logger.info(f"  Unieke besluiten: {len(decisions)}")
                logger.info(f"  Partijen die gestemd hebben:")
                for party, votes_count in sorted(parties.items()):
                    total = sum(votes_count.values())
                    logger.info(f"    {party:25}: {total:3d} stemmen (voor: {votes_count['voor']}, tegen: {votes_count['tegen']}, onthouding: {votes_count['onthouding']})")
                    
        except Exception as e:
            logger.error(f"Fout bij lezen stemming data: {e}")
            
    def find_matching_data(self):
        """Zoek naar moties die ook stemming data hebben"""
        logger.info("\n🔗 Data koppeling verkenning:")
        
        # Probeer te matchen tussen moties en stemmingen
        zaak_dir = self.data_dir / 'zaak'
        stemming_dir = self.data_dir / 'stemming'
        
        if not zaak_dir.exists() or not stemming_dir.exists():
            logger.warning("Kan niet beide directories vinden voor koppeling")
            return
            
        motie_files = list(zaak_dir.glob('moties_page_*.json'))
        voting_files = list(stemming_dir.glob('votes_page_*.json'))
        
        # Verzamel alle Zaak IDs uit moties
        zaak_ids = set()
        for file in motie_files[:2]:  # Eerste 2 bestanden om snelheid
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                for motie in data.get('value', []):
                    zaak_id = motie.get('Id')
                    if zaak_id:
                        zaak_ids.add(zaak_id)
            except:
                continue
                
        logger.info(f"Gevonden {len(zaak_ids)} unieke Zaak IDs in moties")
        
        # Verzamel alle Besluit IDs uit stemmingen
        besluit_ids = set()
        for file in voting_files[:5]:  # Eerste 5 bestanden
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    votes = json.load(f)
                    
                for vote in votes:
                    besluit_id = vote.get('Besluit_Id')
                    if besluit_id:
                        besluit_ids.add(besluit_id)
            except:
                continue
                
        logger.info(f"Gevonden {len(besluit_ids)} unieke Besluit IDs in stemmingen")
        
        # Dit toont de data structuur - we hebben Zaak (moties) en Besluit (stemming resultaten)
        # Later moeten we deze koppelen via andere API endpoints
        
    def run_exploration(self):
        """Voer complete data verkenning uit"""
        logger.info("🔍 Start data verkenning van verzamelde parlementaire data")
        
        # Basis statistieken
        self.get_directory_stats()
        
        # Verken moties
        self.explore_motie_data()
        
        # Verken stemmingen  
        self.explore_voting_data()
        
        # Zoek koppelingen
        self.find_matching_data()
        
        logger.info("\n✅ Data verkenning voltooid!")

if __name__ == "__main__":
    explorer = DataExplorer()
    explorer.run_exploration()