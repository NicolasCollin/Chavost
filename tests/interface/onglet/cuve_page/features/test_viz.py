import unittest
import pandas as pd

from src.interface.onglet.cuve_page.features.viz import (
    build_fig_abc_repartition,
    build_fig_evolution_quantite,
    build_fig_evolution_valeur,
    build_fig_pareto_abc,
    build_fig_top_cuvees,
)


class TestViz(unittest.TestCase):
    """Tests basiques pour viz.py (les fonctions doivent retourner une figure Plotly)."""

    def test_build_fig_top_cuvees(self) -> None:
        """Le top cuvées doit renvoyer une figure même avec peu de données."""
        df = pd.DataFrame({"article": ["A", "B"], "quantite_vendue": [10, 5]})
        fig = build_fig_top_cuvees(df, value_col="quantite_vendue", title="Top")
        self.assertTrue(hasattr(fig, "data"))  # plotly figure

    def test_build_fig_evolution(self) -> None:
        """Les courbes d'évolution doivent renvoyer une figure."""
        df = pd.DataFrame({"mois": ["2025-01", "2025-02"], "quantite_vendue": [10, 20], "valeur_ventes": [100, 200]})
        fig_q = build_fig_evolution_quantite(df)
        fig_v = build_fig_evolution_valeur(df)
        self.assertTrue(hasattr(fig_q, "data"))
        self.assertTrue(hasattr(fig_v, "data"))

    def test_build_fig_pareto_abc(self) -> None:
        """Le pareto doit afficher une courbe (même si minimal)."""
        df = pd.DataFrame({"rang": [1, 2], "cumul_part": [0.6, 1.0]})
        fig = build_fig_pareto_abc(df)
        self.assertTrue(hasattr(fig, "data"))

    def test_build_fig_abc_repartition(self) -> None:
        """La répartition ABC doit produire une figure."""
        df = pd.DataFrame({"classe_abc": ["A", "A", "B", "C"]})
        fig = build_fig_abc_repartition(df)
        self.assertTrue(hasattr(fig, "data"))


if __name__ == "__main__":
    unittest.main()
