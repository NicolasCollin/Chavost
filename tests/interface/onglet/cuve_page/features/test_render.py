import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

from src.interface.onglet.cuve_page.features import render as render_module


class TestRender(unittest.TestCase):
    """Tests basiques pour render.py (on mock Streamlit pour éviter l'UI)."""

    def test_render_kpis_empty(self) -> None:
        """Avec un DataFrame vide, la fonction doit juste afficher une info (pas crash)."""
        df = pd.DataFrame()

        with patch.object(render_module, "st") as st_mock:
            st_mock.info = MagicMock()
            render_module.render_kpis_produits(df)
            st_mock.info.assert_called_once()

    def test_render_kpis_ok(self) -> None:
        """Avec une ligne KPI, la fonction doit appeler metric 4 fois."""
        df = pd.DataFrame(
            [
                {
                    "nb_mouvements": 5,
                    "nb_cuvees": 2,
                    "quantite_vendue": 15,
                    "valeur_ventes": 150.0,
                }
            ]
        )

        with patch.object(render_module, "st") as st_mock:
            cols = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
            st_mock.columns = MagicMock(return_value=cols)
            render_module.render_kpis_produits(df)
            self.assertTrue(cols[0].metric.called)  # simple check
            self.assertTrue(cols[1].metric.called)
            self.assertTrue(cols[2].metric.called)
            self.assertTrue(cols[3].metric.called)

    def test_render_table(self) -> None:
        """render_table doit appeler st.dataframe."""
        df = pd.DataFrame({"a": [1, 2]})

        with patch.object(render_module, "st") as st_mock:
            st_mock.markdown = MagicMock()
            st_mock.dataframe = MagicMock()
            render_module.render_table(df, "Titre")
            st_mock.dataframe.assert_called_once()


if __name__ == "__main__":
    unittest.main()
