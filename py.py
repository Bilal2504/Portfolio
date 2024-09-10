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
df_trie["Charges SI (Interne/Externe) validée"] = df_trie["Charges SI (Interne/Externe) validée"].str.replace(',', '.')
df_trie["Charges SI (Interne/Externe) validée"] = df_trie["Charges SI (Interne/Externe) validée"].fillna(0)
df_trie["Charges SI (Interne/Externe) validée"] = pd.to_numeric(df_trie["Charges SI (Interne/Externe) validée"], errors='coerce')

# Fonction pour ajouter des lignes de somme par sous-domaine et domaine
def ajouter_ligne_somme_par_domaine(df):
    # Liste pour stocker les résultats intermédiaires
    liste_dfs = []
    
    # Grouper par Domaine pour traiter chaque domaine individuellement
    for domaine, groupe_domaine in df.groupby("Domaine"):
        # Grouper par Sous-domaine pour traiter chaque sous-domaine dans ce domaine
        for sous_domaine, groupe_sous_domaine in groupe_domaine.groupby("Sous-domaine"):
            # Calculer la somme des charges pour ce sous-domaine
            somme_sous_domaine = groupe_sous_domaine["Charges SI (Interne/Externe) validée"].sum()
            
            # Ajouter le groupe de sous-domaine
            liste_dfs.append(groupe_sous_domaine)
            
            # Créer une ligne de somme pour le sous-domaine
            ligne_somme_sous_domaine = pd.DataFrame({
                "Type": [""],
                "Projet": [""],
                "Domaine": [domaine],
                "Sous-domaine": [f"Total {sous_domaine}"],
                "Charges SI (Interne/Externe) validée": [somme_sous_domaine],
                "Somme total": [""]
            })
            
            # Ajouter la ligne de somme du sous-domaine
            liste_dfs.append(ligne_somme_sous_domaine)
        
        # Calculer la somme des charges pour le domaine
        somme_domaine = groupe_domaine["Charges SI (Interne/Externe) validée"].sum()
        
        # Créer une ligne de somme pour le domaine
        ligne_somme_domaine = pd.DataFrame({
            "Type": [""],
            "Projet": [""],
            "Domaine": [f"Total {domaine}"],
            "Sous-domaine": [""],
            "Charges SI (Interne/Externe) validée": [somme_domaine],
            "Somme total": [""]
        })
        
        # Ajouter la ligne de somme du domaine
        liste_dfs.append(ligne_somme_domaine)
    
    # Concaténer toutes les parties pour former le DataFrame final
    return pd.concat(liste_dfs, ignore_index=True)

# Appliquer la fonction pour ajouter les lignes de somme
df_final = ajouter_ligne_somme_par_domaine(df_trie)

# Sauvegarder les résultats dans un nouveau fichier CSV
fichier_final = "copsi_mission_test_22.csv"
df_final.to_csv(fichier_final, index=False)

# Confirmation de la création du fichier
print(f"Les colonnes sélectionnées ont été sauvegardées dans {fichier_final}.")
