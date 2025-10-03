import pandas as pd
import json
import os
import sys
import glob
from thefuzz import process

def load_json_to_df(file_path, entity_name):
    """Loads a single JSON file into a pandas DataFrame."""
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return pd.DataFrame()
    
    try:
        df = pd.read_json(file_path, orient='records')
        print(f"Successfully loaded {len(df)} records for {entity_name} from {file_path}")
        return df
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return pd.DataFrame()

def load_full_term_data(directory, entity_name):
    """Loads all 'fullterm' JSON files from a directory into a pandas DataFrame."""
    all_data = []
    file_pattern = os.path.join(directory, '*_fullterm_*.json')
    json_files = glob.glob(file_pattern)
    
    if not json_files:
        print(f"Warning: No JSON files found for {entity_name} in {directory}")
        return pd.DataFrame()

    for file in json_files:
        with open(file, 'r', encoding='utf-8') as f:
            try:
                content = json.load(f)
                if isinstance(content, list):
                    all_data.extend(content)
                elif isinstance(content, dict) and 'value' in content and isinstance(content['value'], list):
                     all_data.extend(content['value'])
            except json.JSONDecodeError:
                print(f"Error decoding JSON from file: {file}")
                
    if not all_data:
        return pd.DataFrame()

    df = pd.json_normalize(all_data)
    print(f"Loaded {len(df)} total records for {entity_name}.")
    return df

def find_best_zaak_match(besluit_tekst, zaak_onderwerpen):
    """Finds the best match for a besluit_tekst from a list of zaak_onderwerpen."""
    if not besluit_tekst or pd.isna(besluit_tekst):
        return None, 0
    
    # The `process.extractOne` function returns a tuple of (match, score)
    best_match = process.extractOne(besluit_tekst, zaak_onderwerpen)
    if best_match:
        return best_match[0], best_match[1]
    return None, 0

def main():
    """
    Links the Stemming-Besluit data with Zaak data using fuzzy text matching.
    """
    base_path = 'c:/motiematcher'
    linkage_file = os.path.join(base_path, 'stemming_besluit_linkage.json')
    zaak_path = os.path.join(base_path, 'bronmateriaal-onbewerkt', 'zaak')
    output_file = os.path.join(base_path, 'final_linked_data.json')
    
    # --- Load Data ---
    print("\n--- Loading Data ---")
    df_linked = load_json_to_df(linkage_file, "Stemming-Besluit Linkage")
    df_zaak = load_full_term_data(zaak_path, "Zaak")

    if df_linked.empty or df_zaak.empty:
        print("Could not load data for linking. Aborting.")
        sys.exit(1)

    # --- Prepare Data for Matching ---
    df_zaak.dropna(subset=['Onderwerp', 'Id'], inplace=True)
    # Create a dictionary for quick lookup: Onderwerp -> Id
    zaak_onderwerp_to_id = pd.Series(df_zaak.Id.values, index=df_zaak.Onderwerp).to_dict()
    zaak_onderwerpen = list(zaak_onderwerp_to_id.keys())

    # --- Fuzzy Matching ---
    print("\n--- Performing Fuzzy Text Matching (this may take a while) ---")
    
    # Apply the matching function to the 'BesluitTekst' column
    matches = df_linked['BesluitTekst'].apply(lambda x: find_best_zaak_match(x, zaak_onderwerpen))

    # Create new columns for the match results
    df_linked['Matched_Zaak_Onderwerp'] = [match[0] for match in matches]
    df_linked['Match_Score'] = [match[1] for match in matches]
    
    # Map the matched onderwerp back to a Zaak_Id
    df_linked['Matched_Zaak_Id'] = df_linked['Matched_Zaak_Onderwerp'].map(zaak_onderwerp_to_id)

    print("Matching complete.")
    
    # --- Filter and Save ---
    # Let's only keep matches with a reasonable score
    high_quality_matches = df_linked[df_linked['Match_Score'] >= 85]
    
    print(f"\nFound {len(high_quality_matches)} high-quality matches (score >= 85).")

    if high_quality_matches.empty:
        print("No high-quality matches found. The output file will not be created.")
        sys.exit(0)
        
    print(f"--- Saving {len(high_quality_matches)} linked records to {output_file} ---")
    high_quality_matches.to_json(output_file, orient='records', indent=4)
    print(f"Successfully created the final linked data file: {output_file}")


if __name__ == "__main__":
    main()
