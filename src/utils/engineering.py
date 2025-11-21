from src.utils.load_files import (
    take_article_file,
    take_client_prosp_file,
    take_stok_file,
)


# Ingénieurie sur la base article_file
def ing_article():
    data = take_article_file()

    # retravail des noms des colonnes.
    data.columns = (
        data.columns.str.strip().str.lower().str.replace(r"[^a-z0-9]+", "_", regex=True)
    )

    # retravail des types selon les variables

    return data


def ing_client():
    data = take_client_prosp_file()

    # retravail des noms des colonnes.
    data.columns = (
        data.columns.str.strip().str.lower().str.replace(r"[^a-z0-9]+", "_", regex=True)
    )

    # retravail des types selon les variables

    return data


def ing_stock_file():
    data = take_stok_file()

    # retravail des noms des colonnes.
    data.columns = (
        data.columns.str.strip().str.lower().str.replace(r"[^a-z0-9]+", "_", regex=True)
    )

    # retravail des types selon les variables

    return data
