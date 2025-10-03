import pandas as pd
import json
import os
import sys

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
    final_df = motions_df[motions_df['Besluit_Id'].isin(close_call_ids)].copy()
    
    # Add the vote counts to the final dataframe for context
    final_df = final_df.merge(vote_counts[['Totaal_Voor', 'Totaal_Tegen', 'Verschil']], on='Besluit_Id', how='left')

    print(f"Final dataset contains {len(final_df)} records.")

    # --- Save Final Filtered Data ---
    print(f"--- Saving {len(final_df)} filtered records to {output_file} ---")
    final_df.to_json(output_file, orient='records', indent=4)
    print(f"Successfully created the final filtered data file: {output_file}")


if __name__ == "__main__":
    main()
