                          Ligne  ... Total BUDGET demandé Réel
0     Projet ou Chantier Projet  ...               K Euros nan
1                      Chantier  ...                       NaN
2                      Chantier  ...                       NaN
3                      Chantier  ...                       NaN
4                      Chantier  ...                       NaN
...                         ...  ...                       ...
5781                   Chantier  ...                       NaN
5782                   Chantier  ...                       NaN
5783                     Projet  ...                       NaN
5784                   Chantier  ...                       NaN
5785                   Chantier  ...                       NaN

[5786 rows x 57 columns]
Voici pourquoi il y'a une erreur corrige
import pandas as pd

# Fonction pour fusionner les deux premières lignes et ensuite les supprimer
def fusionner_lignes(df):
    # Créer une liste qui stockera les valeurs fusionnées des colonnes
    new_columns = []
    
    # Parcourir chaque colonne du DataFrame
    for col in df.columns:
        # Récupérer les valeurs des deux premières lignes pour la colonne actuelle
        ligne_1 = str(df.iloc[0][col]) 
        ligne_2 = str(df.iloc[1][col]) 
        
        # Fusionner les deux lignes avec un espace entre elles, si les deux ne sont pas vides
        fusion = f"{ligne_1} {ligne_2}".strip()
        
        # Ajouter cette fusion à la liste des nouvelles colonnes
        new_columns.append(fusion)
    
    # Ajouter la ligne fusionnée en tant que première ligne (index 0)
    df.loc[-1] = new_columns  # On insère avec un index temporaire négatif
    df = df.sort_index().reset_index(drop=True)  # Réindexer correctement pour déplacer cette ligne en première position

    # Supprimer les deux premières lignes d'origine (celles avec les données originales)
    df = df.drop([1, 2]).reset_index(drop=True)
    
    return df

# Convertir le fichier xls en dataframe (remplacer par le bon chemin)
read_file = pd.read_excel("20240902_etat_validation_paa_chantiers.xls")

# Appliquer la fonction de fusion des deux premières lignes
df_fusion = fusionner_lignes(read_file)

# Sauvegarder le fichier après avoir fusionné les deux premières lignes
df_fusion.to_csv("20240902_etat_validation_paa_chantiers.csv", index=False, header=True)

# Charger le fichier CSV après fusion
df = pd.read_csv("20240902_etat_validation_paa_chantiers.csv")

# Renommage des colonnes
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

# Calcul de la somme totale des charges pour tout le SI
somme_total_si = df_trie["Charges SI (Interne/Externe) validée"].sum()

# Ajouter la somme totale en première ligne
df_trie['Somme total'] = ""
df_trie.loc[df_trie.index[0], "Somme total"] = somme_total_si

# Fonction pour ajouter des lignes de somme par sous-domaine et domaine
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
            "Poids total par sous-domaine": [""],
            "Poids du sous-domaine dans le SI": [""]
        })
        
        liste_dfs.append(ligne_somme_domaine)
    
    return pd.concat(liste_dfs, ignore_index=True)

# Appliquer la fonction pour ajouter les lignes de somme
df_final = ajouter_ligne_somme_par_domaine(df_trie)

# Sauvegarder les résultats dans un nouveau fichier CSV
fichier_final = "copsi_mission_20240918.csv"
df_final.to_csv(fichier_final, index=False)

# Confirmation de la création du fichier
print(f"Les colonnes sélectionnées ont été sauvegardées dans {fichier_final}.")
