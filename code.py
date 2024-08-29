import pandas as pd
import csv

fichier_initial = "20240801_etat_validation_paa_chantiers.csv"

df = pd.read_csv(fichier_initial)


# Parametrage du renommage des colonnes
colonne_extraire = {
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


# Permet d'extraire et renommée les colonnes
df_selection = df[list(colonne_extraire.keys())]
df_selection = df_selection.rename(columns = colonne_extraire)


# Filtre pour garder que les projet de type projet
df_filtre = df_selection[df_selection["Type"] == "Projet"]

# Trier par ordre croissant Domaine puis Sous-domaine
df_trie = df_filtre.sort_values(by = ["Domaine", "Sous-domaine"], ascending = [True, True])

print("avant conversion : ")
print(df_trie["test"]

# Permet de calculer la somme de la colonne (total des charges)
df_trie["Charges SI (Interne/Externe) validée"] = pd.to_numeric(df_trie["Charges SI (Interne/Externe) validée"], errors = 'coerce')

somme_total = df_trie["Charges SI (Interne/Externe) validée"].sum()

df_trie["Somme total"] = ""
df_trie.loc[df_trie.index[0], "Somme total"] = somme_total
                                                                   
# Permet de calculer la somme des charges sous-totaux par doamaine


# Permet de calculer la somme des charges sous-totaux par sous-doamaine


# Permet de calculer le poids des sous-domaine par rapport au SI


# Permet de nommer et envoyer dans le nouveau fichier
fichier_final = "copsi_mission_test_07.csv"
df_trie.to_csv (fichier_final, index = False)

# Retour pour confirmé la création du nouveau fichier
print (f"Les colonnes selectionné ont été sauvegardés dans {fichier_final}.")
