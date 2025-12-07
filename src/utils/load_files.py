import pandas as pd
from pathlib import Path
from typing import Dict

from src.utils.find_path import chemin_fichier
from src.utils.main_engineering import load_csv_safely


#Initialisation des fichier attendus
RAW_DATASETS_KEY = "RAW_DATASETS"
DATA_FOLDER = Path(chemin_fichier())
EXPECTED_FILES = [
    "article_precis_avec_code.xls",
    "base_commande.xls",
    "client_prospect.xls",
    "histo_clients.xls",
    "mouv_stock.xls",
]

def take_all_file():
    dict_data :  Dict[str, pd.DataFrame] = {}
    # Charger les fichiers attendus en mémoire et 
    for fname in EXPECTED_FILES:
        fpath = DATA_FOLDER / fname
        df = load_csv_safely(fpath)
        dict_data[fname] = df
    
    return dict_data


#Chargement de toutes les bases séparéments

def df_commande_file():
    df = take_all_file()['base_commande.xls']
    return df
def df_article_file():
    df = take_all_file()['article_precis_avec_code.xls']
    return df
def df_client_prosp_file():
    df = take_all_file()['client_prospect.xls']
    return df
def df_clients_file():
    df = take_all_file()['histo_clients.xls']
    return df
def df_stok_file():
    df = take_all_file()['mouv_stock.xls']
    return df



