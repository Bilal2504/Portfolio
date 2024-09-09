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
# Remplacement des valeurs vides par un 0
df_trie["Charges SI (Interne/Externe) validée"] = df_trie["Charges SI (Interne/Externe) validée"].fillna(0)

# Conversion de la colonne en type numérique
df_trie["Charges SI (Interne/Externe) validée"] = pd.to_numeric(df_trie["Charges SI (Interne/Externe) validée"], errors='coerce')

# Calcul de la somme totale des charges
somme_total = df_trie["Charges SI (Interne/Externe) validée"].sum()

# Ajouter la somme totale en première ligne
df_trie['Somme total'] = ""
df_trie.loc[df_trie.index[0], "Somme total"] = somme_total

# Calcul des charges totales par Domaine et ajout d'une ligne de somme pour chaque Domaine
def ajouter_ligne_somme_par_domaine(df):
    # Grouper par Domaine
    groupes = df.groupby("Domaine")
    liste_dfs = []
    
    for domaine, groupe in groupes:
        # Calculer la somme des charges pour ce domaine
        somme_domaine = groupe["Charges SI (Interne/Externe) validée"].sum()
        
        # Créer une ligne de somme
        ligne_somme = pd.DataFrame({
            "Type": ["Total"],
            "Projet": [""],
            "Domaine": [domaine],
            "Sous-domaine": [""],
            "Charges SI (Interne/Externe) validée": [somme_domaine],
            "Somme total": [""]
        })
        
        # Ajouter le groupe et la ligne de somme dans une liste
        liste_dfs.append(groupe)
        liste_dfs.append(ligne_somme)
    
    # Concaténer tous les groupes et les lignes de somme dans un seul DataFrame
    return pd.concat(liste_dfs, ignore_index=True)

# Appliquer la fonction pour ajouter les lignes de somme par domaine
df_final = ajouter_ligne_somme_par_domaine(df_trie)

# Sauvegarde des données traitées dans un nouveau fichier CSV
fichier_final = "copsi_mission_test_19.csv"
df_final.to_csv(fichier_final, index=False)

# Confirmation de la création du fichier
print(f"Les colonnes sélectionnées ont été sauvegardées dans {fichier_final}.")