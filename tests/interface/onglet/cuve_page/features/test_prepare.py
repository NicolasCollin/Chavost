import unittest
import pandas as pd

from src.interface.onglet.cuve_page.features.prepare import prepare_cuve_filters


class TestPrepare(unittest.TestCase):
    """Tests basiques pour prepare.py (filtres cuvées + années)."""

    def test_prepare_filters_by_cuvee(self) -> None:
        """Le filtre sur les cuvées doit réduire df_stock et df_article."""
        df_stock = pd.DataFrame(
            {
                "article": ["A", "B", "B"],
                "date": pd.to_datetime(["2025-01-01", "2025-01-02", "2025-02-01"]),
                "quantit_": [-1, -2, -3],
                "valeur_du_mouvement": [-10.0, -20.0, -30.0],
            }
        )
        df_article = pd.DataFrame({"article": ["A", "B", "C"]})
        df_commande = pd.DataFrame({"dummy": [1]})

        df_s, df_a, df_c = prepare_cuve_filters(
            df_stock=df_stock,
            df_article=df_article,
            df_commande=df_commande,
            sel_cuvees=["B"],
            sel_annees=[],
        )

        self.assertEqual(set(df_s["article"].unique().tolist()), {"B"})
        self.assertEqual(set(df_a["article"].unique().tolist()), {"B"})
        self.assertFalse(df_c.empty)

    def test_prepare_filters_by_year(self) -> None:
        """Le filtre sur l'année doit garder uniquement les lignes de l'année demandée."""
        df_stock = pd.DataFrame(
            {
                "article": ["A", "A"],
                "date": pd.to_datetime(["2024-12-31", "2025-01-01"]),
                "quantit_": [-1, -1],
                "valeur_du_mouvement": [-10.0, -10.0],
            }
        )
        df_article = pd.DataFrame({"article": ["A"]})
        df_commande = pd.DataFrame({"dummy": [1]})

        df_s, _, _ = prepare_cuve_filters(
            df_stock=df_stock,
            df_article=df_article,
            df_commande=df_commande,
            sel_cuvees=[],
            sel_annees=[2025],
        )

        self.assertTrue((df_s["date"].dt.year == 2025).all())


if __name__ == "__main__":
    unittest.main()
