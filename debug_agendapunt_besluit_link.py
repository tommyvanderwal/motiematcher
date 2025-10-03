import pandas as pd
import json
import os
import glob

def load_data(directory, file_pattern, entity_name):
    """Loads JSON files from a directory into a pandas DataFrame."""
    all_data = []
    json_files = glob.glob(os.path.join(directory, file_pattern))
    
    if not json_files:
        print(f"No files found for {entity_name} in {directory} with pattern {file_pattern}")
        return pd.DataFrame()

    print(f"Found {len(json_files)} files for {entity_name}.")
    
    for file in json_files:
        with open(file, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                # Handle both list of records and single record per file
                if isinstance(data, list):
                    all_data.extend(data)
                else:
                    all_data.append(data)
            except json.JSONDecodeError:
                print(f"Error decoding JSON from file: {file}")
    
    if not all_data:
        return pd.DataFrame()
        
    df = pd.json_normalize(all_data)
    print(f"Loaded {len(df)} total records for {entity_name}.")
    return df

def main():
    """
    Analyzes the relationship between Agendapunt and Besluit entities.
    """
    base_path = 'c:/motiematcher/bronmateriaal-onbewerkt'
    agendapunt_path = os.path.join(base_path, 'agendapunt')
    besluit_path = os.path.join(base_path, 'besluit')

    # --- Load Data ---
    print("\n--- Loading Data ---")
    df_agendapunt = load_data(agendapunt_path, '*_fullterm_*.json', "Agendapunt")
    df_besluit = load_data(besluit_path, '*_fullterm_*.json', "Besluit")

    if df_agendapunt.empty or df_besluit.empty:
        print("Could not load data for analysis. Exiting.")
        return

    # --- Analyze Columns ---
    print("\n--- Agendapunt Columns ---")
    print(df_agendapunt.columns.tolist())

    print("\n--- Besluit Columns ---")
    print(df_besluit.columns.tolist())

    # --- Inspect Data Samples ---
    print("\n--- Agendapunt Head ---")
    print(df_agendapunt.head())

    print("\n--- Besluit Head ---")
    print(df_besluit.head())

    # --- Search for Linking Keys ---
    print("\n--- Searching for potential linking keys ---")
    agendapunt_ids = set(df_agendapunt['Id'])
    
    # Check if any column in Besluit contains IDs that match Agendapunt IDs
    for col in df_besluit.columns:
        try:
            besluit_values = set(df_besluit[col].dropna())
            if agendapunt_ids.intersection(besluit_values):
                print(f"Potential link found! Column '{col}' in Besluit contains values present in Agendapunt 'Id'.")
                # Let's see how many overlap
                overlap = agendapunt_ids.intersection(besluit_values)
                print(f"  - Overlap count: {len(overlap)}")
                # print(f"  - Example overlapping value: {next(iter(overlap))}")

        except (TypeError, AttributeError):
            # This can happen if the column contains unhashable types like lists
            print(f"Could not check column '{col}' for links (likely complex type).")
            
    # A Besluit is related to a Zaak, and a Zaak has Agendapunten.
    # The link is likely Besluit -> Zaak -> Agendapunt.
    # Let's check if Besluit has a Zaak_Id
    if 'Zaak.Id' in df_besluit.columns:
        print("\nFound 'Zaak.Id' in Besluit. This is a likely link.")
    elif 'Zaak_Id' in df_besluit.columns:
        print("\nFound 'Zaak_Id' in Besluit. This is a likely link.")
    else:
        print("\nCould not find a direct 'Zaak_Id' or 'Zaak.Id' in Besluit.")
        
    if 'Zaak.Id' in df_agendapunt.columns:
        print("Found 'Zaak.Id' in Agendapunt. This confirms the indirect link.")
    elif 'Zaak_Id' in df_agendapunt.columns:
        print("Found 'Zaak_Id' in Agendapunt. This confirms the indirect link.")
    else:
        print("Could not find 'Zaak_Id' or 'Zaak.Id' in Agendapunt.")


if __name__ == "__main__":
    main()
