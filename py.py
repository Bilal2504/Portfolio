import pandas as pd

# Charger le fichier CSV initial
fichier_initial = "20240801_etat_validation_paa_chantiers.csv"
df = pd.read_csv(fichier_initial)

# Paramétrage du renommage des colonnes
colonne_extraire = {
    "Ligne Projet ou Chantier": "Type",
    "Projet / sous-projets Code projet ou sous-projet présent dans le référentiel des projets SI": "Projet",
    "Macro-Domaine": "Domaine",
    "Domaine": "Sous-domaine",
    "Charges Structure MOAE/MOE Valide JH": "Charges SI (Interne/Externe) validée"
}

# Extraction et renommage des colonnes
df_selection = df[list(colonne_extraire.keys())]
df_selection = df_selection.rename(columns=colonne_extraire)

# Filtre pour garder seulement les projets de type "Projet"
df_filtre = df_selection[df_selection["Type"] == "Projet"]

# Trier par ordre croissant Domaine puis Sous-domaine
df_trie = df_filtre.sort_values(by=["Domaine", "Sous-domaine"], ascending=[True, True])

# Nettoyage des données dans la colonne "Charges SI (Interne/Externe) validée"
df_trie["Charges SI (Interne/Externe) validée"] = df_trie["Charges SI (Interne/Externe) validée"].str.strip()  # Suppression des espaces superflus
df_trie["Charges SI (Interne/Externe) validée"] = df_trie["Charges SI (Interne/Externe) validée"].str.replace(' ', '')  # Suppression des espaces entre les chiffres
df_trie["Charges SI (Interne/Externe) validée"] = df_trie["Charges SI (Interne/Externe) validée"].str.replace(',', '')  # Suppression des virgules (séparateurs de milliers)
df_trie["Charges SI (Interne/Externe) validée"] = df_trie["Charges SI (Interne/Externe) validée"].str.replace('€', '')  # Suppression des symboles monétaires

# Conversion de la colonne en type numérique
df_trie["Charges SI (Interne/Externe) validée"] = pd.to_numeric(df_trie["Charges SI (Interne/Externe) validée"], errors='coerce')

# Remplacer les NaN par 0 après la conversion
df_trie["Charges SI (Interne/Externe) validée"].fillna(0, inplace=True)

# Calcul de la somme totale des charges
somme_total = df_trie["Charges SI (Interne/Externe) validée"].sum()

# Calcul des sous-totaux par Domaine et Sous-domaine
df_trie['Charges Domaine'] = df_trie.groupby('Domaine')['Charges SI (Interne/Externe) validée'].transform('sum')
df_trie['Charges Sous-domaine'] = df_trie.groupby('Sous-domaine')['Charges SI (Interne/Externe) validée'].transform('sum')

# Calcul du poids des sous-domaines par rapport à la somme totale
df_trie['Poids Sous-domaine (%)'] = (df_trie['Charges Sous-domaine'] / somme_total) * 100

# Ajouter la somme totale en première ligne (optionnel)
df_trie['Somme total'] = ""
df_trie.loc[df_trie.index[0], "Somme total"] = somme_total

# Sauvegarde des données traitées dans un nouveau fichier CSV
fichier_final = "copsi_mission_test_07.csv"
df_trie.to_csv(fichier_final, index=False)

# Confirmation de la création du fichier
print(f"Les colonnes sélectionnées ont été sauvegardées dans {fichier_final}.")