from src.utils.load_files import (
    df_article_file,
    df_client_prosp_file,
    df_stok_file,
    df_commande_file,
    df_clients_file,
)


# Ingénieurie sur la base article_file
def df_article():
    data = df_article_file()

    # retravail des noms des colonnes.
    data.columns = (
        data.columns.str.strip().str.lower().str.replace(r"[^a-z0-9]+", "_", regex=True)
    )

    # retravail des types selon les variables

    return data


def df_client_prosp():
    data = df_client_prosp_file()

    # retravail des noms des colonnes.
    data.columns = (
        data.columns.str.strip().str.lower().str.replace(r"[^a-z0-9]+", "_", regex=True)
    )

    # retravail des types selon les variables

    return data


def ing_stock():
    data = df_stok_file()

    # retravail des noms des colonnes.
    data.columns = (
        data.columns.str.strip().str.lower().str.replace(r"[^a-z0-9]+", "_", regex=True)
    )

    # retravail des types selon les variables

    return data

def ing_commande():
    data = df_commande_file()

    # retravail des noms des colonnes.
    data.columns = (
        data.columns.str.strip().str.lower().str.replace(r"[^a-z0-9]+", "_", regex=True)
    )

    # retravail des types selon les variables

    return data

def ing_clients():
    data = df_clients_file()

    # retravail des noms des colonnes.
    data.columns = (
        data.columns.str.strip().str.lower().str.replace(r"[^a-z0-9]+", "_", regex=True)
    )

    # retravail des types selon les variables

    return data
