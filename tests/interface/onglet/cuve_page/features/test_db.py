import unittest
import pandas as pd

from src.interface.onglet.cuve_page.features.db import make_con, register_tables


class TestDb(unittest.TestCase):
    """Tests basiques pour db.py (connexion + enregistrement des tables)."""

    def test_make_con(self) -> None:
        """La connexion doit être créée sans erreur."""
        con = make_con()
        self.assertIsNotNone(con)

    def test_register_tables(self) -> None:
        """Les tables stock/article/commande doivent être queryables."""
        con = make_con()

        df_stock = pd.DataFrame(
            {"article": ["A"], "quantit_": [-1], "valeur_du_mouvement": [-10.0]}
        )
        df_article = pd.DataFrame({"article": ["A"]})
        df_commande = pd.DataFrame({"dummy": [1]})

        con = register_tables(con, df_stock, df_article, df_commande)

        out = con.execute("SELECT COUNT(*) AS n FROM stock").df()
        self.assertEqual(int(out.loc[0, "n"]), 1)


if __name__ == "__main__":
    unittest.main()
