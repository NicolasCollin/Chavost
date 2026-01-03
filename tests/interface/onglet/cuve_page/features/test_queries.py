import unittest
import pandas as pd

from src.interface.onglet.cuve_page.features.db import make_con, register_tables
from src.interface.onglet.cuve_page.features.queries import (
    query_abc_cuvees,
    query_evolution_mensuelle,
    query_kpis_produits,
    query_risque_rupture,
    query_top_cuvees_quantite,
    query_top_cuvees_valeur,
)


def build_stock_fixture() -> pd.DataFrame:
    """Petit jeu de données stock (ventes = quantit_ < 0)."""
    return pd.DataFrame(
        {
            "article": ["A", "A", "B", "B", "C"],
            "date": pd.to_datetime(["2025-01-10", "2025-01-20", "2025-02-05", "2025-02-10", "2025-02-12"]),
            "quantit_": [-10, -5, -2, -8, -1],
            "valeur_du_mouvement": [-100.0, -50.0, -20.0, -80.0, -10.0],
        }
    )


class TestQueries(unittest.TestCase):
    """Tests basiques pour queries.py (colonnes attendues + non-crash)."""

    def setUp(self) -> None:
        """Crée une base DuckDB en mémoire et enregistre les tables minimales."""
        self.con = make_con()

        df_stock = build_stock_fixture()
        df_article = pd.DataFrame({"article": ["A", "B", "C"]})
        df_commande = pd.DataFrame({"dummy": [1]})

        self.con = register_tables(self.con, df_stock, df_article, df_commande)

    def test_query_kpis_produits(self) -> None:
        """La requête KPI doit renvoyer 1 ligne avec les colonnes clés."""
        df = query_kpis_produits(self.con)
        self.assertEqual(len(df), 1)
        self.assertTrue({"nb_mouvements", "nb_cuvees", "quantite_vendue", "valeur_ventes"}.issubset(df.columns))

    def test_query_top_quantite(self) -> None:
        """Top quantités doit renvoyer article + quantite_vendue."""
        df = query_top_cuvees_quantite(self.con, top_n=2)
        self.assertTrue({"article", "quantite_vendue"}.issubset(df.columns))
        self.assertLessEqual(len(df), 2)

    def test_query_top_valeur(self) -> None:
        """Top valeur doit renvoyer article + valeur_ventes."""
        df = query_top_cuvees_valeur(self.con, top_n=2)
        self.assertTrue({"article", "valeur_ventes"}.issubset(df.columns))
        self.assertLessEqual(len(df), 2)

    def test_query_evolution_mensuelle(self) -> None:
        """Évolution mensuelle doit fournir mois + deux métriques."""
        df = query_evolution_mensuelle(self.con)
        self.assertTrue({"mois", "quantite_vendue", "valeur_ventes"}.issubset(df.columns))

    def test_query_abc(self) -> None:
        """ABC doit renvoyer A/B/C et cumul_part entre 0 et 1."""
        df = query_abc_cuvees(self.con)
        self.assertTrue({"article", "classe_abc", "cumul_part"}.issubset(df.columns))
        self.assertTrue(set(df["classe_abc"].unique().tolist()).issubset({"A", "B", "C"}))
        self.assertTrue(((df["cumul_part"] >= 0) & (df["cumul_part"] <= 1)).all())

    def test_query_risque_rupture(self) -> None:
        """Risque rupture doit renvoyer les colonnes finales attendues."""
        df = query_risque_rupture(self.con)
        expected = {"article", "stock_actuel", "ventes_30j", "conso_jour", "couverture_jours", "niveau_risque", "recommandation"}
        self.assertTrue(expected.issubset(df.columns))


if __name__ == "__main__":
    unittest.main()
