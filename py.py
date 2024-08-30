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
df_trie["Charges SI (Interne/Externe) validée"] = df_trie["Charges SI (Interne/Externe) validée"].str.strip()
# Remplacement des virgules par des points pour traiter les décimales correctement
df_trie["Charges SI (Interne/Externe) validée"] = df_trie["Charges SI (Interne/Externe) validée"].str.replace(',', '.')

# Conversion de la colonne en type numérique
df_trie["Charges SI (Interne/Externe) validée"] = pd.to_numeric(df_trie["Charges SI (Interne/Externe) validée"], errors='coerce')

# Calcul de la somme totale des charges
somme_total = df_trie["Charges SI (Interne/Externe) validée"].sum()

# Ajouter la somme totale en première ligne (optionnel)
df_trie['Somme total'] = ""
df_trie.loc[df_trie.index[0], "Somme total"] = somme_total

# Calcul des charges totales par Domaine
charges_domaine = df_trie.groupby('Domaine')['Charges SI (Interne/Externe) validée'].sum().reset_index()
charges_domaine['Sous-domaine'] = ''  # Pour que la colonne Sous-domaine soit vide pour les lignes de total
charges_domaine['Type'] = 'Total Domaine'
charges_domaine['Charges SI (Interne/Externe) validée'] = charges_domaine['Charges SI (Interne/Externe) validée']
charges_domaine['Somme total'] = somme_total

# Calcul des charges totales par Sous-domaine
charges_sous_domaine = df_trie.groupby('Sous-domaine')['Charges SI (Interne/Externe) validée'].sum().reset_index()
charges_sous_domaine['Domaine'] = ''  # Pour que la colonne Domaine soit vide pour les lignes de total
charges_sous_domaine['Type'] = 'Total Sous-domaine'
charges_sous_domaine['Charges SI (Interne/Externe) validée'] = charges_sous_domaine['Charges SI (Interne/Externe) validée']
charges_sous_domaine['Somme total'] = somme_total

# Concaténation des sous-totaux au DataFrame principal
df_trie = pd.concat([df_trie, charges_domaine, charges_sous_domaine])

# Trier par Domaine, Sous-domaine pour s'assurer que les totaux apparaissent à la fin des groupes
df_trie = df_trie.sort_values(by=['Domaine', 'Sous-domaine'])

# Calcul du poids des Domaines et Sous-domaines par rapport aux charges totales
df_trie['Poids Domaine (%)'] = df_trie['Domaine'].map(lambda x: (charges_domaine.loc[charges_domaine['Domaine'] == x, 'Charges SI (Interne/Externe) validée'].values[0] / somme_total) * 100 if x else '')
df_trie['Poids Sous-domaine par Domaine (%)'] = (df_trie['Charges SI (Interne/Externe) validée'] / df_trie.groupby('Domaine')['Charges SI (Interne/Externe) validée'].transform('sum')) * 100
df_trie['Poids Sous-domaine (%)'] = df_trie['Sous-domaine'].map(lambda x: (charges_sous_domaine.loc[charges_sous_domaine['Sous-domaine'] == x, 'Charges SI (Interne/Externe) validée'].values[0] / somme_total) * 100 if x else '')

# Sauvegarde des données traitées dans un nouveau fichier CSV
fichier_final = "copsi_mission_test_13.csv"
df_trie.to_csv(fichier_final, index=False)

# Confirmation de la création du fichier
print(f"Les colonnes sélectionnées ont été sauvegardées dans {fichier_final}.")