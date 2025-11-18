"""_summary_ : Ce fichier regarde dans tout l'ordinateur et regarde s'il ets possible de trouver le dossier "test_export"
    Returns: il retourne alors le chelmin entier de l'utilisateur du fichier "test_export"
    
    l'objectif de ce fichier python est alors d'utiliser la fonction en tant que package et pour faire l'import du fichier il sera simplement necessaire de faire
    from src.utils.file import chemin_fichier
"""



import os
from pathlib import Path
import platform

def find_folder(folder_name: str) -> str | None:
    """
    Recherche récursive d'un dossier par nom, compatible Windows / macOS / Linux.
    Retourne le chemin complet du premier dossier trouvé, sinon None.
    """

    system = platform.system()

    # 👉 Point de départ en fonction du système
    if system == "Windows":
        # ex : C:/Users/<name>
        start_paths = [f"{drive}:/" for drive in "C"]
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


def chemin_fichier():
    folder_path = find_folder("test_export")
    return(folder_path)
