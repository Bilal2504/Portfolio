import pandas as pd

# Load the CSV file
fichier_initial = "20240801_etat_validation_paa_chantiers.csv"
df = pd.read_csv(fichier_initial)

# Parameter setting for renaming columns
colonne_extraire = {
    "Ligne Projet ou Chantier": "Type",
    "Projet / sous-projets Code projet ou sous-projet présent dans le référentiel des projets SI": "Projet",
    "Macro-Domaine": "Domaine",
    "Domaine": "Sous-domaine",
    "Charges Structure MOAE/MOE Valide JH": "Charges SI (Interne/Externe) validée"
}

# Extract and rename the selected columns
df_selection = df[list(colonne_extraire.keys())]
df_selection = df_selection.rename(columns=colonne_extraire)

# Filter to keep only the rows of type 'Projet'
df_filtre = df_selection[df_selection["Type"] == "Projet"]

# Sort by 'Domaine' and 'Sous-domaine' in ascending order
df_trie = df_filtre.sort_values(by=["Domaine", "Sous-domaine"], ascending=[True, True])

# Convert the 'Charges SI (Interne/Externe) validée' column to numeric
df_trie["Charges SI (Interne/Externe) validée"] = pd.to_numeric(df_trie["Charges SI (Interne/Externe) validée"], errors='coerce')

# Calculate the total sum of the charges
somme_total = df_trie["Charges SI (Interne/Externe) validée"].sum()

# Add a new column 'Somme total' and place the total sum in the first row
df_trie["Somme total"] = ""
df_trie.at[df_trie.index[0], "Somme total"] = somme_total

# Calculate the subtotal charges by 'Domaine'
df_trie['Charges Domaine'] = df_trie.groupby('Domaine')['Charges SI (Interne/Externe) validée'].transform('sum')

# Calculate the subtotal charges by 'Sous-domaine'
df_trie['Charges Sous-domaine'] = df_trie.groupby('Sous-domaine')['Charges SI (Interne/Externe) validée'].transform('sum')

# Calculate the weight of each 'Sous-domaine' relative to the total SI charges
df_trie['Poids Sous-domaine (%)'] = (df_trie['Charges Sous-domaine'] / somme_total) * 100

# Save the processed data to a new CSV file
fichier_final = "copsi_mission_test_07.csv"
df_trie.to_csv(fichier_final, index=False)

# Confirm the creation of the new file
print(f"Les colonnes sélectionnées ont été sauvegardées dans {fichier_final}.")