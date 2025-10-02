"""
Data Storage System for Parliamentary Data
Handles JSON/CSV output formats and S3 upload functionality
"""

import json
import csv
from typing import List, Dict, Optional
import logging
from datetime import datetime
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class DataStorageManager:
    """Manages storage of parliamentary data in various formats and destinations"""
    
    def __init__(self, bucket_name: Optional[str] = None):
        """
        Initialize storage manager
        
        Args:
            bucket_name: S3 bucket name for data storage
        """
        self.bucket_name = bucket_name
        
        # S3 client will be initialized when needed
        self.s3_client = None
        
        logger.info("Data storage manager initialized (S3 disabled for local testing)")
    
    def export_to_json(self, data: List[Dict], output_path: str) -> bool:
        """
        Export data to JSON format
        
        Args:
            data: List of parliamentary items
            output_path: Local file path for JSON output
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully exported {len(data)} items to JSON: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            return False
    
    def export_to_csv(self, data: List[Dict], output_path: str) -> bool:
        """
        Export data to CSV format (flattened structure)
        
        Args:
            data: List of parliamentary items
            output_path: Local file path for CSV output
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not data:
                logger.warning("No data to export to CSV")
                return False
            
            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Flatten voting records into separate rows
            flattened_data = []
            
            for item in data:
                base_item = {
                    'id': item['id'],
                    'type': item['type'], 
                    'title': item['title'],
                    'summary': item['summary'],
                    'date': item['date'],
                    'proposer': item['proposer'],
                    'status': item['status'],
                    'total_votes_voor': item.get('total_votes_voor', 0),
                    'total_votes_tegen': item.get('total_votes_tegen', 0),
                    'total_votes_onthouding': item.get('total_votes_onthouding', 0),
                    'voting_date': item.get('voting_date', ''),
                    'enrichment_status': item.get('enrichment_status', '')
                }
                
                # Add voting records as separate columns
                voting_records = item.get('voting_records', [])
                if voting_records:
                    for record in voting_records:
                        row = base_item.copy()
                        row.update({
                            'party_name': record.get('party_name', ''),
                            'party_abbreviation': record.get('party_abbreviation', ''),
                            'vote': record.get('vote', ''),
                            'num_members': record.get('num_members', 0)
                        })
                        flattened_data.append(row)
                else:
                    # Add item without voting data
                    row = base_item.copy()
                    row.update({
                        'party_name': '',
                        'party_abbreviation': '',
                        'vote': '',
                        'num_members': 0
                    })
                    flattened_data.append(row)
            
            # Write CSV
            if flattened_data:
                fieldnames = flattened_data[0].keys()
                
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(flattened_data)
                
                logger.info(f"Successfully exported {len(flattened_data)} rows to CSV: {output_path}")
                return True
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return False
    
    def create_web_ready_data(self, enriched_data: List[Dict]) -> Dict:
        """
        Create optimized data structure for web consumption
        
        Args:
            enriched_data: List of enriched parliamentary items
            
        Returns:
            Dictionary with optimized structure for web APIs
        """
        # Separate items by type for easier web consumption
        web_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_items': len(enriched_data),
                'types': {}
            },
            'items': enriched_data,
            'parties': {},
            'summary_stats': {}
        }
        
        # Count items by type
        type_counts = {}
        for item in enriched_data:
            item_type = item['type']
            type_counts[item_type] = type_counts.get(item_type, 0) + 1
        
        web_data['metadata']['types'] = type_counts
        
        # Extract party information
        parties = {}
        for item in enriched_data:
            voting_records = item.get('voting_records', [])
            for record in voting_records:
                party_abbr = record.get('party_abbreviation')
                if party_abbr and party_abbr not in parties:
                    parties[party_abbr] = {
                        'abbreviation': party_abbr,
                        'full_name': record.get('party_name', ''),
                        'member_count': record.get('num_members', 0)
                    }
        
        web_data['parties'] = parties
        
        # Calculate summary statistics
        total_votes_voor = sum(item.get('total_votes_voor', 0) for item in enriched_data)
        total_votes_tegen = sum(item.get('total_votes_tegen', 0) for item in enriched_data)
        total_votes_onthouding = sum(item.get('total_votes_onthouding', 0) for item in enriched_data)
        
        web_data['summary_stats'] = {
            'total_votes_voor': total_votes_voor,
            'total_votes_tegen': total_votes_tegen, 
            'total_votes_onthouding': total_votes_onthouding,
            'enriched_items': len([item for item in enriched_data if item.get('enrichment_status') == 'completed'])
        }
        
        return web_data
    
    def save_complete_dataset(self, enriched_data: List[Dict], 
                            output_dir: str = 'output',
                            upload_to_s3: bool = False) -> Dict[str, str]:
        """
        Save complete dataset in multiple formats and optionally upload to S3
        
        Args:
            enriched_data: List of enriched parliamentary items
            output_dir: Local output directory
            upload_to_s3: Whether to upload files to S3
            
        Returns:
            Dictionary with paths/URLs of created files
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # File paths
        json_path = f"{output_dir}/parliamentary_data_{timestamp}.json"
        csv_path = f"{output_dir}/parliamentary_data_{timestamp}.csv"
        web_json_path = f"{output_dir}/web_data_{timestamp}.json"
        
        results = {}
        
        # Export to JSON
        if self.export_to_json(enriched_data, json_path):
            results['json_local'] = json_path
        
        # Export to CSV
        if self.export_to_csv(enriched_data, csv_path):
            results['csv_local'] = csv_path
        
        # Create web-optimized data
        web_data = self.create_web_ready_data(enriched_data)
        if self.export_to_json(web_data, web_json_path):
            results['web_json_local'] = web_json_path
        
        logger.info(f"Dataset saved successfully: {results}")
        return results

def main():
    """Main execution function for data storage"""
    # Load enriched data
    try:
        with open('output/enriched_parliamentary_data.json', 'r', encoding='utf-8') as f:
            enriched_data = json.load(f)
        
        # Initialize storage manager
        storage_manager = DataStorageManager(
            bucket_name='motiematcher-data'  # Replace with actual bucket name
        )
        
        # Save dataset in multiple formats
        results = storage_manager.save_complete_dataset(
            enriched_data=enriched_data,
            upload_to_s3=False  # Set to True when S3 is configured
        )
        
        print("Data storage completed:")
        for format_type, path in results.items():
            print(f"  {format_type}: {path}")
            
    except FileNotFoundError:
        logger.error("Enriched data file not found. Run enrichment pipeline first.")
    except Exception as e:
        logger.error(f"Error in data storage: {e}")

if __name__ == "__main__":
    main()