import pandas as pd

# Charger le fichier CSV
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

# Extraire et renommer les colonnes
df_selection = df[list(colonne_extraire.keys())]
df_selection = df_selection.rename(columns=colonne_extraire)

# Filtrer pour ne garder que les lignes de type 'Projet'
df_filtre = df_selection[df_selection["Type"] == "Projet"]

# Convertir la colonne des charges en numérique (en gérant les erreurs)
df_filtre["Charges SI (Interne/Externe) validée"] = pd.to_numeric(df_filtre["Charges SI (Interne/Externe) validée"], errors='coerce')

# Vérifier que la conversion en numérique a fonctionné
print(df_filtre["Charges SI (Interne/Externe) validée"].head())

# Calculer la somme totale des charges
somme_total = df_filtre["Charges SI (Interne/Externe) validée"].sum()

# Ajouter une colonne 'Somme total' et y placer la somme totale dans la première ligne
df_filtre["Somme total"] = ""
df_filtre.at[df_filtre.index[0], "Somme total"] = somme_total

# Calculer les sous-totaux des charges par 'Domaine'
df_filtre['Charges Domaine'] = df_filtre.groupby('Domaine')['Charges SI (Interne/Externe) validée'].transform('sum')

# Calculer les sous-totaux des charges par 'Sous-domaine'
df_filtre['Charges Sous-domaine'] = df_filtre.groupby('Sous-domaine')['Charges SI (Interne/Externe) validée'].transform('sum')

# Calculer le poids des sous-domaines par rapport à la somme totale
df_filtre['Poids Sous-domaine (%)'] = (df_filtre['Charges Sous-domaine'] / somme_total) * 100

# Vérifier que les nouvelles colonnes ont été calculées correctement
print(df_filtre[['Domaine', 'Sous-domaine', 'Charges Domaine', 'Charges Sous-domaine', 'Poids Sous-domaine (%)']].head())

# Trier par 'Domaine' et 'Sous-domaine'
df_trie = df_filtre.sort_values(by=["Domaine", "Sous-domaine"], ascending=[True, True])

# Sauvegarder les données traitées dans un nouveau fichier CSV
fichier_final = "copsi_mission_test_07.csv"
df_trie.to_csv(fichier_final, index=False)

# Confirmation de la création du fichier
print(f"Les colonnes sélectionnées ont été sauvegardées dans {fichier_final}.")