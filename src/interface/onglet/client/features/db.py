
import duckdb


def make_con():
    """Crée une connexion DuckDB en mémoire."""
    con = duckdb.connect(database=":memory:")
    return con


def register_tables(con, df_com_filtre, df_filtre, df_stock_filtred):
    """Enregistre les tables DuckDB avec les mêmes noms que ton script."""
    con.register("commandes_select", df_com_filtre)
    con.register("clients_select", df_filtre)
    con.register("stock_select", df_stock_filtred)
    return con