"""
Tests unitaires pour les requêtes SQL de queries.py.

Ces tests valident le résultat des KPI calculés par les requêtes :
- les colonnes retournées (schéma attendu)
- une règle métier simple par KPI (filtrage, agrégation, somme)

Les données sont créées en mémoire et enregistrées dans DuckDB afin de rendre
les tests rapides et reproductibles (aucun accès au disque).
"""

import duckdb
import pandas as pd

from src.interface.onglet.client_page.features.queries import (
    query_nb_commande,
    query_suivi_temp,
    query_top_achat,
    query_tot_paye,
)


def _prepare_test_con():
    """
    Crée une connexion DuckDB en mémoire avec des tables minimales de test.
    """
    con = duckdb.connect(database=":memory:")

    commandes = pd.DataFrame(
        {
            "n_document": ["CM001", "FA001", "XX001"],
            "nom_du_client": ["A", "A", "B"],
            "net_payer": [100.0, 200.0, 50.0],
        }
    )

    stock = pd.DataFrame(
        {
            "nom_du_client": ["A", "A", "B"],
            "article": ["X", "Y", "X"],
            "quantit_": [-2, -3, -1],
            "mois_annee": ["2025-01", "2025-02", "2025-01"],
        }
    )

    con.register("commandes_select", commandes)
    con.register("stock_select", stock)

    return con


class TestKpiCommandes:
    """Vérifications liées aux KPI de commandes (compteurs de documents)."""

    def test_query_nb_commande_compte_uniquement_cm_et_fa(self):
        """Vérifie que le compteur inclut uniquement les documents CM* et FA* (et exclut les autres)."""
        con = _prepare_test_con()

        df = query_nb_commande(con)

        assert list(df.columns) == ["nb_comm", "nom"]
        assert df.loc[df["nom"] == "A", "nb_comm"].iloc[0] == 2
        assert "B" not in df["nom"].values


class TestKpiPaiements:
    """Vérifications liées aux KPI de paiement (totaux par client)."""

    def test_query_tot_paye_somme_correctement_par_client(self):
        """Vérifie que le total payé est la somme de net_payer, regroupée par client."""
        con = _prepare_test_con()

        df = query_tot_paye(con)

        assert list(df.columns) == ["tot_paye", "nom"]
        assert df.loc[df["nom"] == "A", "tot_paye"].iloc[0] == 300.0
        assert df.loc[df["nom"] == "B", "tot_paye"].iloc[0] == 50.0


class TestKpiStock:
    """Vérifications liées aux KPI stock (suivi mensuel et agrégation par article)."""

    def test_query_suivi_temp_agrege_par_mois_et_client(self):
        """Vérifie l'agrégation des quantités par client et par mois_annee (suivi temporel)."""
        con = _prepare_test_con()

        df = query_suivi_temp(con)

        assert list(df.columns) == ["nom", "quantite", "mois_annee"]
        assert len(df) == 3

        row = df[(df["nom"] == "A") & (df["mois_annee"] == "2025-01")]
        assert row.iloc[0]["quantite"] == 2

    def test_query_top_achat_agrege_par_article_et_client(self):
        """Vérifie l'agrégation des quantités par client et par article (top achats)."""
        con = _prepare_test_con()

        df = query_top_achat(con)

        assert list(df.columns) == ["article", "quantite_tot", "nom"]

        row = df[(df["nom"] == "A") & (df["article"] == "X")]
        assert row.iloc[0]["quantite_tot"] == 2