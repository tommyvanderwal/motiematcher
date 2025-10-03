import pandas as pd
import json
import os
import glob
import sys

def load_full_term_data(directory, entity_name):
    """
    Loads all JSON files from a directory into a pandas DataFrame.
    Adjusts file pattern for stemming_complete.
    """
    all_data = []
    
    if entity_name == 'Stemming':
        file_pattern = os.path.join(directory, 'stemming_page_*_complete_*.json')
    else:
        file_pattern = os.path.join(directory, '*_fullterm_*.json')

    json_files = glob.glob(file_pattern)
    
    if not json_files:
        print(f"Warning: No JSON files found for {entity_name} with pattern '{os.path.basename(file_pattern)}' in {directory}")
        return pd.DataFrame()

    print(f"Found {len(json_files)} files for {entity_name}.")
    
    for file in json_files:
        with open(file, 'r', encoding='utf-8') as f:
            try:
                content = json.load(f)
                if isinstance(content, list):
                    all_data.extend(content)
                elif isinstance(content, dict) and 'value' in content and isinstance(content['value'], list):
                     all_data.extend(content['value'])
                else:
                    all_data.append(content)
            except json.JSONDecodeError:
                print(f"Error decoding JSON from file: {file}")
                
    if not all_data:
        print(f"No data loaded for {entity_name}.")
        return pd.DataFrame()

    df = pd.json_normalize(all_data)
    print(f"Loaded {len(df)} total records for {entity_name}.")
    return df

def main():
    """
    Main function to perform the data loading, merging, and saving.
    Revised logic: Create a reliable base link between Stemming and Besluit.
    """
    base_path = 'c:/motiematcher/bronmateriaal-onbewerkt'
    besluit_path = os.path.join(base_path, 'besluit')
    stemming_path = os.path.join(base_path, 'stemming_complete')
    output_file = 'c:/motiematcher/stemming_besluit_linkage.json'

    # --- Data Loading ---
    print("\n--- Loading Data ---")
    df_besluit = load_full_term_data(besluit_path, "Besluit")
    df_stemming = load_full_term_data(stemming_path, "Stemming")

    # --- Validation ---
    if df_besluit.empty or df_stemming.empty:
        print("Critical data is missing. One or more DataFrames are empty. Aborting.")
        if df_besluit.empty: print("Besluit DataFrame is empty.")
        if df_stemming.empty: print("Stemming DataFrame is empty.")
        sys.exit(1)

    # --- Data Cleaning and Preparation ---
    print("\n--- Cleaning and Preparing Data ---")
    
    required_besluit_cols = ['Id', 'BesluitSoort', 'Status']
    required_stemming_cols = ['Besluit_Id', 'Soort', 'ActorFractie']
    
    if not all(col in df_besluit.columns for col in required_besluit_cols):
        print(f"Besluit DataFrame missing one of required columns: {required_besluit_cols}. Found: {df_besluit.columns.tolist()}")
        sys.exit(1)
        
    if not all(col in df_stemming.columns for col in required_stemming_cols):
        print(f"Stemming DataFrame missing one of required columns: {required_stemming_cols}. Found: {df_stemming.columns.tolist()}")
        sys.exit(1)

    df_besluit.dropna(subset=required_besluit_cols, inplace=True)
    df_stemming.dropna(subset=required_stemming_cols, inplace=True)

    # --- Merging Logic ---
    print("\n--- Merging DataFrames (Stemming -> Besluit) ---")
    
    df_final = pd.merge(
        df_stemming,
        df_besluit,
        left_on='Besluit_Id',
        right_on='Id',
        how='inner',
        suffixes=('_stemming', '_besluit')
    )
    print(f"Result after Stemming-Besluit merge: {len(df_final)} rows.")

    if df_final.empty:
        print("Merge between Stemming and Besluit resulted in an empty DataFrame. No common Besluit_Id found. Aborting.")
        sys.exit(1)

    # --- Save Final Linked Data ---
    print(f"\n--- Saving {len(df_final)} linked records to {output_file} ---")
    df_final.to_json(output_file, orient='records', indent=4)
    print(f"Successfully created the linked data file: {output_file}")

if __name__ == "__main__":
    main()
