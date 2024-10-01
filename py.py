import pandas as pd

# Fonction pour fusionner la ligne d'en-tête avec la première ligne de données
def fusionner_header_ligne(df):
    # Fonction pour nettoyer les colonnes 'Unnamed' et garder les données significatives
    def nettoyer_colonne(col):
        if col.startswith("Unnamed:"):
            # Supprimer "Unnamed: [chiffre]" et garder uniquement le texte après
            return col.split(maxsplit=1)[-1] if len(col.split(maxsplit=1)) > 1 else ""
        return col
    
    # Nettoyer les noms de colonnes en supprimant 'Unnamed' tout en gardant les données utiles
    df.columns = [nettoyer_colonne(col) for col in df.columns]
    
    # Récupérer la ligne actuelle d'en-tête (noms des colonnes)
    header_row = list(df.columns)
    
    # Récupérer la première ligne de données (index 0)
    first_data_row = df.iloc[0]
    
    # Fusionner la ligne d'en-tête et la première ligne de données
    new_header = [f"{header} {data}".strip() if header else f"{data}".strip() for header, data in zip(header_row, first_data_row)]
    
    # Assigner la ligne fusionnée comme nouvelle ligne d'en-tête
    df.columns = new_header
    
    # Supprimer la première ligne de données (car elle est fusionnée dans l'en-tête)
    df = df.drop(0).reset_index(drop=True)

    print(df)
    return df

# Charger le fichier Excel
read_file = pd.read_excel("20240902_etat_validation_paa_chantiers.xls")

# Appliquer la fonction pour fusionner l'en-tête et la première ligne
df_fusion = fusionner_header_ligne(read_file)

# Sauvegarder le résultat au format CSV
df_fusion.to_csv("20240902_etat_validation_paa_chantiers.csv", index=False)

# Renommer les colonnes selon le script précédent
colonne_extraire = {
    "Ligne Projet ou Chantier": "Type",
    "Projet / sous-projets Code projet ou sous-projet présent dans le référentiel des projets SI": "Projet",
    "Macro-Domaine": "Domaine",
    "Domaine": "Sous-domaine",
    "Charges Structure MOAE/MOE Valide JH": "Charges SI (Interne/Externe) validée"
}

# Extraire et renommer les colonnes
df_selection = df_fusion[list(colonne_extraire.keys())]
df_selection = df_selection.rename(columns=colonne_extraire)

# Filtrer pour ne garder que les projets de type "Projet"
df_filtre = df_selection[df_selection["Type"] == "Projet"]

# Trier par Domaine et Sous-domaine
df_trie = df_filtre.sort_values(by=["Domaine", "Sous-domaine"], ascending=[True, True])

# Nettoyer la colonne "Charges SI (Interne/Externe) validée"
df_trie["Charges SI (Interne/Externe) validée"] = df_trie["Charges SI (Interne/Externe) validée"].astype(str).str.strip()
df_trie["Charges SI (Interne/Externe) validée"] = df_trie["Charges SI (Interne/Externe) validée"].astype(str).str.replace(',', '.')
df_trie["Charges SI (Interne/Externe) validée"] = df_trie["Charges SI (Interne/Externe) validée"].astype(str).fillna(0)
df_trie["Charges SI (Interne/Externe) validée"] = pd.to_numeric(df_trie["Charges SI (Interne/Externe) validée"], errors='coerce')

# Calculer la somme totale des charges pour l'ensemble du SI
somme_total_si = df_trie["Charges SI (Interne/Externe) validée"].sum()

# Ajouter la somme totale à la première ligne
df_trie['Somme total'] = ""
df_trie.loc[df_trie.index[0], "Somme total"] = somme_total_si

# Fonction pour ajouter des lignes de somme pour chaque domaine et sous-domaine
def ajouter_ligne_somme_par_domaine(df):
    liste_dfs = []
    
    # Grouper par domaine
    for domaine, groupe_domaine in df.groupby("Domaine"):
        somme_domaine = groupe_domaine["Charges SI (Interne/Externe) validée"].sum()
        poids_domaine = round((somme_domaine / somme_total_si) * 100 , 2)
        
        # Grouper par sous-domaine
        for sous_domaine, groupe_sous_domaine in groupe_domaine.groupby("Sous-domaine"):
            somme_sous_domaine = round(groupe_sous_domaine["Charges SI (Interne/Externe) validée"].sum(), 2)
            if somme_domaine != 0:
                poids_sous_domaine = round((somme_sous_domaine / somme_domaine) * 100 , 2)
            else:
                poids_sous_domaine = 0.0
            poids_sous_domaine_si = round((somme_sous_domaine / somme_total_si) * 100 , 2) 
            
            liste_dfs.append(groupe_sous_domaine)
            
            # Ajouter la ligne de somme pour le sous-domaine
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
        
        # Ajouter la ligne de somme pour le domaine
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

# Appliquer la fonction pour ajouter des lignes de somme
df_final = ajouter_ligne_somme_par_domaine(df_trie)

# Sauvegarder les résultats finaux dans un nouveau fichier CSV
fichier_final = "copsi_mission_20241001.csv"
df_final.to_csv(fichier_final, index=False)

# Confirmation de la création du fichier
print(f"Les colonnes sélectionnées ont été sauvegardées dans {fichier_final}.")