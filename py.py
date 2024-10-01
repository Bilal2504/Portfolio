 import pandas as pd

# Fonction pour créer une troisième ligne avec la fusion des deux premières lignes et supprimer les deux premières lignes
def fusionner_lignes(df):
    # Créer une nouvelle liste de colonnes fusionnées
    new_columns = []
    
    for col in df.columns:
        # Fusionner la première et la deuxième ligne, même si l'une des deux est vide
        ligne_1 = str(df[col].iloc[0]).strip() if not pd.isna(df[col].iloc[0]) else ""
        ligne_2 = str(df[col].iloc[1]).strip() if not pd.isna(df[col].iloc[1]) else ""
        
        # Fusionner les deux lignes avec un espace entre elles
        fusion = f"{ligne_1} {ligne_2}".strip()
    
        # Ajouter cette fusion à la liste des nouvelles colonnes
        new_columns.append(fusion)
    
    # Insérer la fusion comme première ligne
    df.loc[-1] = new_columns  # Ajoute la ligne fusionnée au DataFrame
    df.index = df.index + 1   # Incrémenter les indices pour insérer la nouvelle ligne au début
    df = df.sort_index()      # Réorganiser les indices pour placer la nouvelle ligne en première position
    
    # Supprimer les deux premières lignes d'origine (lignes 0 et 1 avant ajout de la ligne fusionnée)
    df = df.drop([1, 2]).reset_index(drop=True)
    
    return df

# Convertir le fichier xls en dataframe
read_file = pd.read_excel("20240902_etat_validation_paa_chantiers.xls")

# Appliquer la fonction de fusion des deux premières lignes
df_fusion = fusionner_lignes(read_file)

# Sauvegarder le fichier après avoir fusionné les deux premières lignes
df_fusion.to_csv("20240902_etat_validation_paa_chantiers.csv", index=False, header=True)

# Confirmation de la création du fichier CSV
print("Les deux premières lignes ont été fusionnées et sauvegardées.")





import pandas as pd

# Fonction pour fusionner les deux premières lignes de chaque colonne en conservant les noms des deux
def fusionner_lignes(df):
    # Créer une nouvelle liste de colonnes fusionnées
    new_columns = []
    
    for col in df.columns:
        # Fusionner la première et la deuxième ligne, même si l'une des deux est vide
        ligne_1 = str(df[col].iloc[0]).strip() if not pd.isna(df[col].iloc[0]) else ""
        ligne_2 = str(df[col].iloc[1]).strip() if not pd.isna(df[col].iloc[1]) else ""
        
        # Fusionner les deux lignes avec un espace entre elles
        fusion = f"{ligne_1} {ligne_2}".strip()
    
        # Ajouter cette fusion à la liste des nouvelles colonnes
        new_columns.append(fusion)    

    return df

# Convertir le fichier xls en dataframe
read_file = pd.read_excel("20240902_etat_validation_paa_chantiers.xls")

# Appliquer la fonction de fusion des deux premières lignes
df_fusion = fusionner_lignes(read_file)

# Sauvegarder le fichier après avoir fusionné les deux premières lignes
df_fusion.to_csv("20240902_etat_validation_paa_chantiers.csv", index=False, header=True)

# Charger le fichier CSV après fusion
df = pd.read_csv("20240902_etat_validation_paa_chantiers.csv")

# Renommage des colonnes comme dans l'exemple précédent
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
