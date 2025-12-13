import pandas as pd
from pathlib import Path
from typing import Dict


from src.utils.main_engineering import load_csv_safely

import os
import json
import platform

chemin_fichier_json = "secrets/chemins.json"


def charger_chemins():
    """Charge les chemins déjà enregistrés dans le fichier JSON."""
    if os.path.exists(chemin_fichier_json):
        with open(chemin_fichier_json, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []  # Si le JSON est corrompu, on repart sur un cache vide  # plus sûr
    return []


def enregistrer_chemins(chemins):
    """Enregistre les chemins dans le fichier JSON."""
    with open(chemin_fichier_json, "w") as f:
        json.dump(chemins, f, indent=4)


def find_folder(folder_name: str) -> str | None:
    """
    Recherche récursive d'un dossier par nom, compatible Windows / macOS / Linux.
    Retourne le chemin complet du premier dossier trouvé, sinon None.
    """

    system = platform.system()

    # Point de départ en fonction du système
    if system == "Windows":
        # ex : C:/Users/<name>
        start_paths = [f"{drive}:/Users/" for drive in "C"]
    else:
        # macOS & Linux → on démarre directement depuis la racine utilisateur
        start_paths = [str(Path.home())]

    for start_path in start_paths:
        if not os.path.exists(start_path):
            continue

        for root, dirs, files in os.walk(start_path):
            if folder_name in dirs:
                return os.path.join(root, folder_name)

    return None


def dossier_valide(
    folder_path: str, expected_files: list[str] | None
) -> bool:  # expected_files peut être None  # typage correct
    """Vérifie que le dossier existe ET contient tous les fichiers attendus (rapide)."""
    p = Path(folder_path)

    # check dossier
    try:
        if not p.is_dir():
            return False
    except OSError:
        return False

    # si aucun fichier attendu, juste l'existence du dossier suffit
    if not expected_files:
        return True  # None signifie aucune contrainte sur les fichiers  # typage sûr

    # 1 seul accès disque: on récupère les noms présents dans le dossier
    try:
        present = {entry.name for entry in os.scandir(p)}
    except OSError:
        return False

    return set(expected_files).issubset(present)


def chemin_fichier(
    folder_name: str = "test_export", expected_files: list[str] | None = None
) -> str | None:
    """
    1) Teste d'abord tous les chemins enregistrés (rapide)
    2) Sinon, cherche dans l'ordi (lent) puis enregistre
    """

    chemins = charger_chemins()

    #  1) Test rapide sur tous les chemins enregistrés
    bool_test = 0
    for base in chemins:
        base_path = Path(base)

        # si le JSON contient déjà .../test_export
        if dossier_valide(str(base_path), expected_files):
            bool_test = 1
            return str(base_path)

        # sinon si le JSON contient un parent
        candidate = base_path / folder_name
        if dossier_valide(str(candidate), expected_files):
            bool_test = 1
            return str(candidate)

    # 2) Rien trouvé → recherche lente dans l'ordinateur
    if bool_test == 0:
        found = find_folder(folder_name)
        if found and dossier_valide(found, expected_files):
            # On sauvegarde (en évitant les doublons)
            if found not in chemins:
                chemins.append(found)
                enregistrer_chemins(chemins)
            return found

    return None


# Initialisation des fichier attendus
RAW_DATASETS_KEY = "RAW_DATASETS"
EXPECTED_FILES = [
    "article_precis_avec_code.xls",
    "base_commande.xls",
    "client_prospect.xls",
    "histo_clients.xls",
    "mouv_stock.xls",
]
_data_folder = chemin_fichier("test_export", EXPECTED_FILES)
if _data_folder is None:
    raise FileNotFoundError(
        "test_export folder not found"
    )  # évite Path(None)  # erreur explicite
DATA_FOLDER = Path(_data_folder)


def take_all_file():
    dict_data: Dict[str, pd.DataFrame] = {}
    # Charger les fichiers attendus en mémoire et
    for fname in EXPECTED_FILES:
        fpath = DATA_FOLDER / fname
        df = load_csv_safely(fpath)
        dict_data[fname] = df

    return dict_data


# Chargement de toutes les bases séparéments


def df_commande_file():
    df = take_all_file()["base_commande.xls"]
    return df


def df_article_file():
    df = take_all_file()["article_precis_avec_code.xls"]
    return df


def df_client_prosp_file():
    df = take_all_file()["client_prospect.xls"]
    return df


def df_clients_file():
    df = take_all_file()["histo_clients.xls"]
    return df


def df_stok_file():
    df = take_all_file()["mouv_stock.xls"]
    return df
