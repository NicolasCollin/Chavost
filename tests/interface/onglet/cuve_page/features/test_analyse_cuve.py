import unittest

import pandas as pd

from src.interface.onglet.cuve_page.features.analyse_cuve import (
    make_con,
    register_tables,
    query_kpis_produits,
    query_abc_cuvees,
    query_risque_rupture,
)


def build_stock_fixture() -> pd.DataFrame:
    """
    Construit un jeu de données minimal de mouvements de stock.

    Convention utilisée dans l'application :
    - une vente est une sortie de stock : quantit_ < 0
    - valeur_du_mouvement suit généralement le signe de la quantité (souvent négatif en sortie)
    """
    return pd.DataFrame(
        {
            "article": ["A", "A", "B", "B", "C"],
            "date": pd.to_datetime(
                ["2025-01-10", "2025-01-20", "2025-02-05", "2025-02-10", "2025-02-12"]
            ),
            "quantit_": [-10, -5, -2, -8, -1],
            "valeur_du_mouvement": [-100.0, -50.0, -20.0, -80.0, -10.0],
        }
    )


def build_article_fixture() -> pd.DataFrame:
    """
    Construit un DataFrame article minimal.

    Note :
    - L'analyse actuelle s'appuie surtout sur la table stock,
      mais on conserve article pour respecter la structure de l'app.
    """
    return pd.DataFrame({"article": ["A", "B", "C"]})


def build_commande_fixture() -> pd.DataFrame:
    """
    Construit un DataFrame commande minimal.

    Note :
    - Utile pour l'enregistrement des tables et pour des évolutions futures
      (ex : relier stock <-> commandes).
    """
    return pd.DataFrame({"dummy": [1]})


class TestAnalyseCuve(unittest.TestCase):
    """
    Tests unitaires (très basiques) de l'analyse des cuvées.

    Objectif :
    - Vérifier que les requêtes SQL renvoient des DataFrames exploitables
    - Vérifier les colonnes attendues (pour éviter des crashs côté UI)
    - Ne pas tester Streamlit, uniquement la logique data
    """

    def setUp(self) -> None:
        """Prépare une base DuckDB en mémoire et enregistre des tables de test."""
        self.con = make_con()

        df_stock = build_stock_fixture()
        df_article = build_article_fixture()
        df_commande = build_commande_fixture()

        # On enregistre les tables avec les noms attendus par nos requêtes : stock, article, commande
        self.con = register_tables(
            con=self.con,
            df_stock=df_stock,
            df_article=df_article,
            df_commande=df_commande,
        )

    def test_query_kpis_produits(self) -> None:
        """
        Vérifie que la requête KPI renvoie une seule ligne avec les colonnes nécessaires.
        """
        df = query_kpis_produits(self.con)

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 1)

        expected_cols = {"nb_mouvements", "nb_cuvees", "quantite_vendue", "valeur_ventes"}
        self.assertTrue(expected_cols.issubset(set(df.columns)))

    def test_query_abc_cuvees(self) -> None:
        """
        Vérifie que l'ABC :
        - renvoie les colonnes clés
        - produit des classes uniquement dans A/B/C
        """
        df = query_abc_cuvees(self.con)

        self.assertIsInstance(df, pd.DataFrame)
        self.assertGreaterEqual(len(df), 1)

        expected_cols = {"article", "valeur_ventes", "rang", "cumul_part", "classe_abc"}
        self.assertTrue(expected_cols.issubset(set(df.columns)))

        classes = set(df["classe_abc"].dropna().unique().tolist())
        self.assertTrue(classes.issubset({"A", "B", "C"}))

    def test_query_risque_rupture(self) -> None:
        """
        Vérifie que la requête 'risque de rupture' renvoie bien les colonnes finales attendues.
        """
        df = query_risque_rupture(self.con)

        self.assertIsInstance(df, pd.DataFrame)

        expected_cols = {
            "article",
            "stock_actuel",
            "ventes_30j",
            "conso_jour",
            "couverture_jours",
            "niveau_risque",
            "recommandation",
        }
        self.assertTrue(expected_cols.issubset(set(df.columns)))


if __name__ == "__main__":
    unittest.main()
