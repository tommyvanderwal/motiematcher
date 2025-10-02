"""
Main ETL Pipeline Runner
Orchestrates the complete data collection and enrichment process
"""

import logging
import sys
from pathlib import Path

# Add project directories to Python path
sys.path.append(str(Path(__file__).parent))

from data_collection.parliamentary_scraper import ParliamentaryScraper
from data_processing.enrichment_pipeline import VotingDataEnricher
from data_processing.storage_manager import DataStorageManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('output/etl_pipeline.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_pilot_pipeline(upload_to_s3: bool = False):
    """
    Run the complete ETL pipeline for pilot data (200 items)
    
    Args:
        upload_to_s3: Whether to upload results to S3
    """
    logger.info("=== Starting MotieMatcher ETL Pipeline (Pilot Mode) ===")
    
    try:
        # Step 1: Data Collection
        logger.info("Step 1: Collecting parliamentary data...")
        scraper = ParliamentaryScraper()
        raw_items = scraper.collect_all_data(pilot_mode=True)
        
        if not raw_items:
            logger.error("No data collected. Stopping pipeline.")
            return False
        
        logger.info(f"Collected {len(raw_items)} items")
        
        # Save raw data
        import json
        raw_data_output = []
        for item in raw_items:
            raw_data_output.append({
                'id': item.id,
                'type': item.type,
                'title': item.title,
                'summary': item.summary,
                'date': item.date,
                'proposer': item.proposer,
                'status': item.status,
                'text_url': item.text_url,
                'voting_url': item.voting_url
            })
        
        with open('output/raw_parliamentary_data.json', 'w', encoding='utf-8') as f:
            json.dump(raw_data_output, f, indent=2, ensure_ascii=False)
        
        # Step 2: Data Enrichment
        logger.info("Step 2: Enriching data with voting records...")
        enricher = VotingDataEnricher()
        enricher.enrich_dataset(
            input_file='output/raw_parliamentary_data.json',
            output_file='output/enriched_parliamentary_data.json'
        )
        
        # Step 3: Data Storage & Export
        logger.info("Step 3: Saving data in multiple formats...")
        
        # Load enriched data
        with open('output/enriched_parliamentary_data.json', 'r', encoding='utf-8') as f:
            enriched_data = json.load(f)
        
        # Initialize storage manager
        storage_manager = DataStorageManager(
            bucket_name='motiematcher-data'  # Configure in production
        )
        
        # Save in multiple formats
        results = storage_manager.save_complete_dataset(
            enriched_data=enriched_data,
            upload_to_s3=upload_to_s3
        )
        
        # Step 4: Generate Summary Report
        logger.info("Step 4: Generating summary report...")
        generate_summary_report(enriched_data, results)
        
        logger.info("=== ETL Pipeline completed successfully ===")
        return True
        
    except Exception as e:
        logger.error(f"ETL Pipeline failed: {e}")
        return False

def generate_summary_report(enriched_data, storage_results):
    """Generate a summary report of the ETL process"""
    from datetime import datetime
    
    # Calculate statistics
    total_items = len(enriched_data)
    type_counts = {}
    status_counts = {}
    party_vote_counts = {}
    
    for item in enriched_data:
        # Count by type
        item_type = item['type']
        type_counts[item_type] = type_counts.get(item_type, 0) + 1
        
        # Count by enrichment status
        status = item.get('enrichment_status', 'unknown')
        status_counts[status] = status_counts.get(status, 0) + 1
        
        # Count party votes
        voting_records = item.get('voting_records', [])
        for record in voting_records:
            party = record.get('party_abbreviation', 'Unknown')
            vote = record.get('vote', 'unknown')
            
            if party not in party_vote_counts:
                party_vote_counts[party] = {'voor': 0, 'tegen': 0, 'onthouding': 0}
            
            if vote in party_vote_counts[party]:
                party_vote_counts[party][vote] += 1
    
    # Generate report
    report = f"""
# MotieMatcher ETL Pipeline Summary Report
Generated: {datetime.now().isoformat()}

## Data Collection Summary
- **Total Items Collected:** {total_items}
- **Items by Type:**
"""
    
    for item_type, count in type_counts.items():
        report += f"  - {item_type}: {count}\n"
    
    report += f"""
## Enrichment Summary
- **Items by Enrichment Status:**
"""
    
    for status, count in status_counts.items():
        report += f"  - {status}: {count}\n"
    
    report += f"""
## Top Party Voting Patterns
"""
    
    # Show top 5 most active parties
    sorted_parties = sorted(party_vote_counts.items(), 
                          key=lambda x: sum(x[1].values()), 
                          reverse=True)[:5]
    
    for party, votes in sorted_parties:
        total_votes = sum(votes.values())
        report += f"- **{party}** (total: {total_votes}): Voor: {votes['voor']}, Tegen: {votes['tegen']}, Onthouding: {votes['onthouding']}\n"
    
    report += f"""
## Output Files Generated
"""
    
    for format_type, path in storage_results.items():
        report += f"- **{format_type}:** {path}\n"
    
    # Save report
    with open('output/pipeline_summary_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    logger.info("Summary report saved to: output/pipeline_summary_report.md")
    print(report)

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='MotieMatcher ETL Pipeline')
    parser.add_argument('--upload-s3', action='store_true', 
                       help='Upload results to S3 (requires AWS configuration)')
    parser.add_argument('--full-mode', action='store_true',
                       help='Run full pipeline (10 years of data) instead of pilot mode')
    
    args = parser.parse_args()
    
    if args.full_mode:
        logger.warning("Full mode not implemented yet. Running pilot mode.")
    
    # Run pipeline
    success = run_pilot_pipeline(upload_to_s3=args.upload_s3)
    
    if success:
        print("\n✅ ETL Pipeline completed successfully!")
        print("Check the 'output/' directory for generated files.")
    else:
        print("\n❌ ETL Pipeline failed. Check logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()