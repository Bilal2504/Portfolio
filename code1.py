import pandas as pd

# Charger le fichier CSV initial
fichier_initial = "20240801_etat_validation_paa_chantiers.csv"  # Remplacez par le chemin de votre fichier
df = pd.read_csv(fichier_initial)

# Sélectionner les colonnes à extraire et les renommer
colonnes_a_extraire = {
    "Ligne Projet ou Chantier":
        "Type",
    "Projet / sous-projets Code projet ou sous-projet présent dans le référentiel des projets SI":
        "Projet",
    "Macro-Domaine":
        "Domaine",
    "Domaine":
        "Sous-domaine",
    "Charges Structure MOAE/MOE Valide JH":
        "Charges SI (Interne/Externe) validée"
}

# Sélectionner les colonnes nécessaires
df_selection = df[list(colonnes_a_extraire.keys())]
df_selection = df_selection.rename(columns=colonnes_a_extraire)  # Renommer les colonnes

# Convertir "nouveau_nom4" (anciennement "nom_colonne_initiale4") en numérique
df_selection["Charges SI (Interne/Externe) validée"] = pd.to_numeric(df_selection["Charges SI (Interne/Externe) validée"], errors='coerce')

# Trier les données : d'abord par "nouveau_nom1", puis par "nouveau_nom2"
df_trie = df_selection.sort_values(by=["Domaine", "Sous-domaine"], ascending=[True, True])

# Diagnostiquer avant la conversion de la colonne 'test'
print("Avant conversion :")
print(df_trie['test'].head(10))  # Affiche les 10 premières valeurs de la colonne 'test'

# Convertir la colonne 'test' en numérique en traitant les erreurs
df_trie['test_num'] = pd.to_numeric(df_trie['test'], errors='coerce')

# Diagnostiquer après la conversion
print("Après conversion :")
print(df_trie[['test', 'test_num']].head(10))  # Compare les anciennes et nouvelles valeurs

# Vérifier si des valeurs valides existent après conversion
if df_trie['test_num'].isna().sum() < len(df_trie):
    # Calculer la somme de la colonne 'test_num' en excluant les NaN
    somme_test = df_trie['test_num'].sum()

    # Ajouter une nouvelle colonne 'somme total' avec la somme calculée seulement sur la première ligne
    df_trie["somme_total"] = ""
    df_trie.loc[df_trie.index[0], ""] = somme_total

    # Sauvegarder les données modifiées dans un nouveau fichier CSV
    fichier_sortie = "copsi_mission_test_09.csv"
    df_trie.to_csv(fichier_sortie, index=False)

    print(f"La somme de la colonne 'test' a été ajoutée dans la première ligne de la colonne 'somme_total' dans {fichier_sortie}.")
else:
    print("Erreur : toutes les valeurs de la colonne 'test' sont devenues NaN après la conversion.")
