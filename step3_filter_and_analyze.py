import pandas as pd
import json
import os
import sys

from typing import List

def main():
    """
    Filters and analyzes the linked data to find 'close call' motions.
    """
    base_path = 'c:/motiematcher'
    input_file = os.path.join(base_path, 'final_linked_data.json')
    output_file = os.path.join(base_path, 'final_filtered_data.json')

    # --- Load Data ---
    print(f"\n--- Loading data from {input_file} ---")
    if not os.path.exists(input_file):
        print(f"Error: Input file not found at {input_file}. Aborting.")
        sys.exit(1)
    
    df = pd.read_json(input_file, orient='records')
    print(f"Successfully loaded {len(df)} records.")

    # --- 1. Filter on 'Soort' (Keep only Motions) ---
    print("\n--- Step 1: Filtering for 'Motie' type ---")
    
    # Rename columns to match the expected names from previous steps if necessary
    if 'Soort_zaak' not in df.columns and 'Matched_Zaak_Soort' in df.columns:
        df.rename(columns={'Matched_Zaak_Soort': 'Soort_zaak'}, inplace=True)
    
    # Now perform the filtering
    if 'Soort_zaak' in df.columns:
        motions_df = df[df['Soort_zaak'] == 'Motie'].copy()
        print(f"Found {len(motions_df)} records of type 'Motie'.")
    else:
        # As a fallback, let's check for 'Soort_besluit_stemming' or similar columns
        # This part of the code is adapted from the user's request to handle variations in column names
        if 'Soort_besluit_stemming' in df.columns:
             motions_df = df[df['Soort_besluit_stemming'] == 'Motie'].copy()
             print(f"Found {len(motions_df)} records of type 'Motie' using 'Soort_besluit_stemming' column.")
        else:
            print("Warning: 'Soort_zaak' or 'Soort_besluit_stemming' column not found. Assuming all records are motions.")
            motions_df = df.copy()


    if motions_df.empty:
        print("No motions found after filtering. Aborting.")
        sys.exit(0)

    # --- 2. Analyze Votes per Besluit_Id ---
    print("\n--- Step 2: Analyzing votes per Besluit_Id ---")
    
    # Ensure correct column names for vote analysis
    if 'Soort_stemming' not in motions_df.columns and 'Soort' in motions_df.columns:
        motions_df.rename(columns={'Soort': 'Soort_stemming'}, inplace=True)
    if 'FractieGrootte' not in motions_df.columns:
         print("Error: 'FractieGrootte' column is required for vote analysis but not found. Aborting.")
         sys.exit(1)


    vote_counts = motions_df.pivot_table(
        index='Besluit_Id',
        columns='Soort_stemming',
        values='FractieGrootte',
        aggfunc='sum',
        fill_value=0
    )
    
    # Ensure 'Voor' and 'Tegen' columns exist
    if 'Voor' not in vote_counts.columns:
        vote_counts['Voor'] = 0
    if 'Tegen' not in vote_counts.columns:
        vote_counts['Tegen'] = 0
        
    vote_counts['Totaal_Voor'] = vote_counts['Voor']
    vote_counts['Totaal_Tegen'] = vote_counts['Tegen']
    
    print(f"Analyzed votes for {len(vote_counts)} unique Besluit_Id's.")
    print(vote_counts.head())

    # --- 3. 'Close Call' Filter ---
    print("\n--- Step 3: Filtering for 'close calls' (difference <= 20) ---")
    vote_counts['Verschil'] = abs(vote_counts['Totaal_Voor'] - vote_counts['Totaal_Tegen'])
    
    close_call_besluiten = vote_counts[vote_counts['Verschil'] <= 20]
    print(f"Found {len(close_call_besluiten)} Besluit_Id's that are 'close calls'.")

    if close_call_besluiten.empty:
        print("No 'close call' motions found. The output file will not be created.")
        sys.exit(0)
        
    close_call_ids = close_call_besluiten.index

    # --- 4. Final Result ---
    print("\n--- Step 4: Preparing final dataset ---")
    close_call_votes = motions_df[motions_df['Besluit_Id'].isin(close_call_ids)].copy()

    # Select a single metadata record per Besluit_Id so the output is deduplicated
    metadata_columns: List[str] = [
        'Besluit_Id',
        'Id_besluit',
        'BesluitTekst',
        'BesluitSoort',
        'Status',
        'StemmingsSoort',
        'Matched_Zaak_Id',
        'Matched_Zaak_Onderwerp',
        'Match_Score',
        'GewijzigdOp_besluit',
        'ApiGewijzigdOp_besluit',
        'AgendapuntZaakBesluitVolgorde'
    ]

    existing_metadata_cols = [col for col in metadata_columns if col in close_call_votes.columns]
    metadata_df = close_call_votes[existing_metadata_cols].copy()

    if 'GewijzigdOp_besluit' in metadata_df.columns:
        metadata_df['_sort_key'] = pd.to_datetime(metadata_df['GewijzigdOp_besluit'], errors='coerce')
    else:
        metadata_df['_sort_key'] = pd.NaT

    metadata_df.sort_values(by=['Besluit_Id', '_sort_key'], ascending=[True, False], inplace=True)
    metadata_df = metadata_df.drop_duplicates(subset=['Besluit_Id'], keep='first')
    metadata_df.drop(columns=['_sort_key'], inplace=True)

    # Aggregate per-party vote details to enrich the dataset downstream
    vote_detail_cols = [col for col in ['ActorNaam', 'Soort_stemming', 'FractieGrootte'] if col in close_call_votes.columns]
    if vote_detail_cols:
        vote_breakdown = (
            close_call_votes.groupby('Besluit_Id')[vote_detail_cols]
            .apply(lambda grp: grp.sort_values(by=vote_detail_cols).to_dict(orient='records'))
            .reset_index(name='Stemverdeling')
        )
    else:
        vote_breakdown = pd.DataFrame(columns=['Besluit_Id', 'Stemverdeling'])

    summary_df = vote_counts[['Totaal_Voor', 'Totaal_Tegen', 'Verschil']].reset_index()
    final_df = metadata_df.merge(summary_df, on='Besluit_Id', how='left')
    if not vote_breakdown.empty:
        final_df = final_df.merge(vote_breakdown, on='Besluit_Id', how='left')

    # Deduplicate on Matched_Zaak_Id while keeping track of all related besluiten
    if 'Matched_Zaak_Id' in final_df.columns:
        besluit_lists = (
            final_df.groupby('Matched_Zaak_Id')['Besluit_Id']
            .apply(list)
            .reset_index(name='Gerelateerde_Besluit_Ids')
        )
        final_df = final_df.merge(besluit_lists, on='Matched_Zaak_Id', how='left')

        if 'GewijzigdOp_besluit' in final_df.columns:
            final_df['_zaak_sort_key'] = pd.to_datetime(final_df['GewijzigdOp_besluit'], errors='coerce')
        else:
            final_df['_zaak_sort_key'] = pd.NaT

        final_df.sort_values(by=['Matched_Zaak_Id', '_zaak_sort_key'], ascending=[True, False], inplace=True)
        final_df = final_df.drop_duplicates(subset=['Matched_Zaak_Id'], keep='first')
        final_df.drop(columns=['_zaak_sort_key'], inplace=True)

    print(f"Final dataset contains {len(final_df)} unieke zaken.")

    # --- Save Final Filtered Data ---
    print(f"--- Saving {len(final_df)} filtered records to {output_file} ---")
    final_df.to_json(output_file, orient='records', indent=4)
    print(f"Successfully created the final filtered data file: {output_file}")


if __name__ == "__main__":
    main()
