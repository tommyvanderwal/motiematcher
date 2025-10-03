import pandas as pd
import json
import os
import glob

def analyze_entity_links(directory, file_pattern, entity_name):
    """
    Loads a sample of data for an entity and prints its structure,
    columns, and potential nested linking keys.
    """
    json_files = glob.glob(os.path.join(directory, file_pattern))
    
    if not json_files:
        print(f"No files found for {entity_name} in {directory} with pattern {file_pattern}")
        return

    print(f"--- Analyzing {entity_name} ---")
    
    # Load data from the first file found
    file_to_inspect = json_files[0]
    print(f"Inspecting file: {os.path.basename(file_to_inspect)}")
    
    with open(file_to_inspect, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print(f"Error decoding JSON from file: {file_to_inspect}")
            return
            
    if not data:
        print("File is empty.")
        return
        
    # Normalize the data to a DataFrame to see the columns
    df = pd.json_normalize(data)
    print("\nAvailable columns:")
    print(df.columns.tolist())
    
    # Print the first few records to inspect content
    print(f"\nSample records from {entity_name}:")
    print(df.head().to_markdown())

    # Specifically look for columns that might contain links (ending in 'Id' or being lists/dicts)
    print("\nPotential linking columns:")
    for col in df.columns:
        if col.endswith('Id') or col.endswith('_Id'):
            print(f"- Found potential ID column: {col}")
        
        # Check for columns that might contain nested objects with IDs
        sample_value = df[col].dropna().iloc[0] if not df[col].dropna().empty else None
        if isinstance(sample_value, list) and sample_value:
            if isinstance(sample_value[0], dict):
                print(f"- Found column with a list of objects: '{col}'. Keys in first object: {sample_value[0].keys()}")
        elif isinstance(sample_value, dict):
             print(f"- Found column with a dictionary object: '{col}'. Keys: {sample_value.keys()}")


def main():
    """
    Analyzes the relationship between Zaak, Activiteit, and Agendapunt.
    """
    base_path = 'c:/motiematcher/bronmateriaal-onbewerkt'
    
    # Analyze Activiteit
    analyze_entity_links(
        os.path.join(base_path, 'activiteit'),
        '*_fullterm_*.json',
        "Activiteit"
    )
    
    # Analyze Agendapunt as well, to be sure
    analyze_entity_links(
        os.path.join(base_path, 'agendapunt'),
        '*_fullterm_*.json',
        "Agendapunt"
    )
    
    # And Zaak, to see how it might link out
    analyze_entity_links(
        os.path.join(base_path, 'zaak'),
        '*_fullterm_*.json',
        "Zaak"
    )


if __name__ == "__main__":
    main()
