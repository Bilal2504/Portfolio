import pandas as pd

# Charger le fichier CSV initial
fichier_initial = "votre_fichier.csv"  # Remplacez par le chemin de votre fichier
df = pd.read_csv(fichier_initial)

# Sélectionner les colonnes à extraire et les renommer
colonnes_a_extraire = {
    "nom_colonne_initiale1": "nouveau_nom1",
    "nom_colonne_initiale2": "nouveau_nom2",
    "nom_colonne_initiale3": "nouveau_nom3",
    "nom_colonne_initiale4": "nouveau_nom4",  # Cette colonne sera convertie en numérique
    "test": "test"  # Garder la colonne 'test' pour calculer la somme
}

# Sélectionner les colonnes nécessaires
df_selection = df[list(colonnes_a_extraire.keys())]
df_selection = df_selection.rename(columns=colonnes_a_extraire)  # Renommer les colonnes

# Convertir "nouveau_nom4" (anciennement "nom_colonne_initiale4") en numérique
df_selection["nouveau_nom4"] = pd.to_numeric(df_selection["nouveau_nom4"], errors='coerce')

# Trier les données : d'abord par "nouveau_nom1", puis par "nouveau_nom2"
df_trie = df_selection.sort_values(by=["nouveau_nom1", "nouveau_nom2"], ascending=[True, True])

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

    # Ajouter une nouvelle colonne 'l'âge test2' avec la somme calculée seulement sur la première ligne
    df_trie["l'âge test2"] = ""
    df_trie.loc[df_trie.index[0], "l'âge test2"] = somme_test

    # Sauvegarder les données modifiées dans un nouveau fichier CSV
    fichier_sortie = "copsi_mission.csv"
    df_trie.to_csv(fichier_sortie, index=False)

    print(f"La somme de la colonne 'test' a été ajoutée dans la première ligne de la colonne 'l'âge test2' dans {fichier_sortie}.")
else:
    print("Erreur : toutes les valeurs de la colonne 'test' sont devenues NaN après la conversion.")