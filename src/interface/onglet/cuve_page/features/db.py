import duckdb
import pandas as pd


def make_con() -> duckdb.DuckDBPyConnection:
    """Crée une connexion DuckDB en mémoire (usage analyse)."""
    return duckdb.connect(database=":memory:")


def register_tables(
    con: duckdb.DuckDBPyConnection,
    df_stock: pd.DataFrame,
    df_article: pd.DataFrame,
    df_commande: pd.DataFrame,
) -> duckdb.DuckDBPyConnection:
    """
    Enregistre les DataFrames dans DuckDB.

    Tables attendues par les requêtes :
    - stock
    - article
    - commande
    """
    con.register("stock", df_stock)
    con.register("article", df_article)
    con.register("commande", df_commande)
    return con
