"""
Tests unitaires pour les fonctions liées à la gestion de DuckDB (db.py).

Ces tests vérifient :
- la création d'une connexion DuckDB en mémoire
- l'enregistrement de DataFrames pandas en tables DuckDB
- la conservation du schéma et du nombre de lignes lors de l'enregistrement
"""

import pandas as pd
from duckdb import DuckDBPyConnection

from src.interface.onglet.client_page.features.db import make_con, register_tables


class TestMakeCon:
    """Vérifications liées à la création de la connexion DuckDB."""

    def test_retourne_une_connexion_duckdb(self):
        """Vérifie que la fonction retourne bien un objet connexion DuckDB."""
        con = make_con()

        assert isinstance(con, DuckDBPyConnection)

    def test_utilise_une_base_en_memoire(self):
        """Vérifie que la connexion utilise une base DuckDB en mémoire."""
        con = make_con()

        databases = con.execute("PRAGMA database_list;").fetchall()
        files = [db[2] for db in databases]

        assert any(f in (None, "", ":memory:") for f in files)


class TestRegisterTables:
    """Vérifications liées à l'enregistrement des tables DuckDB."""

    def test_cree_les_tables_attendues(self):
        """Vérifie que les trois tables DuckDB attendues sont bien créées."""
        con = make_con()

        df_commandes = pd.DataFrame({"order_id": [1, 2], "amount": [10.0, 20.0]})
        df_clients = pd.DataFrame(
            {"client_id": ["A", "B"], "city": ["Reims", "Epernay"]}
        )
        df_stock = pd.DataFrame({"sku": ["X1"], "qty": [5]})

        register_tables(con, df_commandes, df_clients, df_stock)

        tables = [row[0] for row in con.execute("SHOW TABLES;").fetchall()]
        assert "commandes_select" in tables
        assert "clients_select" in tables
        assert "stock_select" in tables

    def test_conserve_le_nombre_de_lignes(self):
        """Vérifie que le nombre de lignes est conservé lors de l'enregistrement."""
        con = make_con()

        df_commandes = pd.DataFrame(
            {"order_id": [1, 2], "amount": [10.0, 20.0]}
        )  # 2 lignes
        df_clients = pd.DataFrame(
            {"client_id": ["A", "B"], "city": ["Reims", "Epernay"]}
        )  # 2 lignes
        df_stock = pd.DataFrame({"sku": ["X1"], "qty": [5]})  # 1 ligne

        register_tables(con, df_commandes, df_clients, df_stock)

        assert con.execute("SELECT COUNT(*) FROM commandes_select;").fetchone()[0] == 2
        assert con.execute("SELECT COUNT(*) FROM clients_select;").fetchone()[0] == 2
        assert con.execute("SELECT COUNT(*) FROM stock_select;").fetchone()[0] == 1

    def test_conserve_les_noms_de_colonnes(self):
        """Vérifie que les noms des colonnes sont conservés lors de l'enregistrement."""
        con = make_con()

        df_commandes = pd.DataFrame({"order_id": [1], "amount": [10.0]})
        df_clients = pd.DataFrame({"client_id": ["A"], "city": ["Reims"]})
        df_stock = pd.DataFrame({"sku": ["X1"], "qty": [5]})

        register_tables(con, df_commandes, df_clients, df_stock)

        commandes_cols = [
            c[1]
            for c in con.execute("PRAGMA table_info('commandes_select');").fetchall()
        ]
        clients_cols = [
            c[1] for c in con.execute("PRAGMA table_info('clients_select');").fetchall()
        ]
        stock_cols = [
            c[1] for c in con.execute("PRAGMA table_info('stock_select');").fetchall()
        ]

        assert commandes_cols == ["order_id", "amount"]
        assert clients_cols == ["client_id", "city"]
        assert stock_cols == ["sku", "qty"]
