import pandas as pd

# Function to merge the header row with the first data row
def fusionner_header_ligne(df):
    # Remove columns with "Unnamed" in their name
    df.columns = [col if not col.startswith("Unnamed:") else "" for col in df.columns]
    
    # Get the current header row (column names)
    header_row = list(df.columns)
    
    # Get the first data row (index 0)
    first_data_row = df.iloc[0]
    
    # Merge the header row and the first data row
    new_header = [f"{header} {data}".strip() if header else "" for header, data in zip(header_row, first_data_row)]
    
    # Assign the merged row as the new column names
    df.columns = new_header
    
    # Drop the first data row (since it's merged into the header now)
    df = df.drop(0).reset_index(drop=True)

    print(df)
    return df

# Load the Excel file
read_file = pd.read_excel("20240902_etat_validation_paa_chantiers.xls")

# Apply the function to merge the header and the first row
df_fusion = fusionner_header_ligne(read_file)

# Save the result to CSV
df_fusion.to_csv("20240902_etat_validation_paa_chantiers.csv", index=False)

# Renaming columns as per your earlier script
colonne_extraire = {
    "Ligne Projet ou Chantier": "Type",
    "Projet / sous-projets Code projet ou sous-projet présent dans le référentiel des projets SI": "Projet",
    "Macro-Domaine": "Domaine",
    "Domaine": "Sous-domaine",
    "Charges Structure MOAE/MOE Valide JH": "Charges SI (Interne/Externe) validée"
}

# Extract and rename columns
df_selection = df_fusion[list(colonne_extraire.keys())]
df_selection = df_selection.rename(columns=colonne_extraire)

# Filter to keep only projects of type "Projet"
df_filtre = df_selection[df_selection["Type"] == "Projet"]

# Sort by Domaine and Sous-domaine
df_trie = df_filtre.sort_values(by=["Domaine", "Sous-domaine"], ascending=[True, True])

# Clean the "Charges SI (Interne/Externe) validée" column
df_trie["Charges SI (Interne/Externe) validée"] = df_trie["Charges SI (Interne/Externe) validée"].astype(str).str.strip()
df_trie["Charges SI (Interne/Externe) validée"] = df_trie["Charges SI (Interne/Externe) validée"].astype(str).str.replace(',', '.')
df_trie["Charges SI (Interne/Externe) validée"] = df_trie["Charges SI (Interne/Externe) validée"].astype(str).fillna(0)
df_trie["Charges SI (Interne/Externe) validée"] = pd.to_numeric(df_trie["Charges SI (Interne/Externe) validée"], errors='coerce')

# Calculate the total sum of charges for the entire SI
somme_total_si = df_trie["Charges SI (Interne/Externe) validée"].sum()

# Add total sum to the first row
df_trie['Somme total'] = ""
df_trie.loc[df_trie.index[0], "Somme total"] = somme_total_si

# Function to add sum rows for each domain and subdomain
def ajouter_ligne_somme_par_domaine(df):
    liste_dfs = []
    
    for domaine, groupe_domaine in df.groupby("Domaine"):
        somme_domaine = groupe_domaine["Charges SI (Interne/Externe) validée"].sum()
        poids_domaine = round((somme_domaine / somme_total_si) * 100 , 2)
        
        for sous_domaine, groupe_sous_domaine in groupe_domaine.groupby("Sous-domaine"):
            somme_sous_domaine = round(groupe_sous_domaine["Charges SI (Interne/Externe) validée"].sum(), 2)
            if somme_domaine != 0:
                poids_sous_domaine = round((somme_sous_domaine / somme_domaine) * 100 , 2)
            else:
                poids_sous_domaine = 0.0
            poids_sous_domaine_si = round((somme_sous_domaine / somme_total_si) * 100 , 2) 
            
            liste_dfs.append(groupe_sous_domaine)
            
            ligne_somme_sous_domaine = pd.DataFrame({
                "Type": [""],
                "Projet": [""],
                "Domaine": [""],
                "Sous-domaine": [f"{sous_domaine}"],
                "Charges SI (Interne/Externe) validée": [""],
                "Somme total": [""],
                "Total domaine": [""],
                "Total sous-domaine": [f"{somme_sous_domaine}"],
                "Poids total par domaine": [""],
                "Poids total par sous-domaine": [f"{poids_sous_domaine}%"],
                "Poids du sous-domaine dans le SI": [f"{poids_sous_domaine_si}%"]
            })
            
            liste_dfs.append(ligne_somme_sous_domaine)
        
        ligne_somme_domaine = pd.DataFrame({
            "Type": [""],
            "Projet": [""],
            "Domaine": [f"{domaine}"],
            "Sous-domaine": [""],
            "Charges SI (Interne/Externe) validée": [""],
            "Somme total": [""],
            "Total domaine": [f"{somme_domaine}"],
            "Total sous-domaine": [""],
            "Poids total par domaine": [f"{poids_domaine}%"],
            "Poids du sous-domaine dans le SI": [""]
        })
        
        liste_dfs.append(ligne_somme_domaine)
    
    return pd.concat(liste_dfs, ignore_index=True)

# Apply the function to add sum rows
df_final = ajouter_ligne_somme_par_domaine(df_trie)

# Save the final results to a new CSV file
fichier_final = "copsi_mission_20241001.csv"
df_final.to_csv(fichier_final, index=False)

# Confirmation of file creation
print(f"Les colonnes sélectionnées ont été sauvegardées dans {fichier_final}.")