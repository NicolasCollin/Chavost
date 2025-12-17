"""
Tests unitaires pour les fonctions de visualisation (viz.py).

Ces tests vérifient que :
- les fonctions retournent bien des objets Plotly Figure
- les colonnes attendues sont bien utilisées (axes / regroupements)
- la structure des figures reste cohérente (ex : une trace par client)

Ces tests ne valident pas le rendu graphique, uniquement la structure
et la cohérence des figures générées.
"""

import pandas as pd
import plotly.graph_objects as go

from src.interface.onglet.client_page.features.viz import (
    build_fig_suivi,
    build_fig_top_achat,
)


class TestBuildFigSuivi:
    """Vérifications de la figure de suivi temporel (courbe)."""

    def test_retourne_une_figure_plotly(self):
        """Vérifie que build_fig_suivi retourne un objet Plotly Figure."""
        df = pd.DataFrame(
            {
                "nom": ["A", "A", "B"],
                "mois_annee": ["2025-01", "2025-02", "2025-01"],
                "quantite": [5, 3, 7],
            }
        )

        fig = build_fig_suivi(df)

        assert isinstance(fig, go.Figure)

    def test_structure_une_trace_par_client(self):
        """Vérifie qu'il y a une trace par client (colonne 'nom')."""
        df = pd.DataFrame(
            {
                "nom": ["A", "B"],
                "mois_annee": ["2025-01", "2025-01"],
                "quantite": [5, 7],
            }
        )

        fig = build_fig_suivi(df)

        assert len(fig.data) == df["nom"].nunique()
        assert fig.data[0].x is not None
        assert fig.data[0].y is not None


class TestBuildFigTopAchat:
    """Vérifications de la figure des achats (barres)."""

    def test_retourne_une_figure_plotly(self):
        """Vérifie que build_fig_top_achat retourne un objet Plotly Figure."""
        df = pd.DataFrame(
            {
                "nom": ["A", "A", "B"],
                "article": ["X", "Y", "X"],
                "quantite_tot": [2, 3, 1],
            }
        )

        fig = build_fig_top_achat(df)

        assert isinstance(fig, go.Figure)

    def test_contient_des_axes_x_et_y(self):
        """Vérifie que la figure contient bien des données sur les axes X et Y."""
        df = pd.DataFrame(
            {
                "nom": ["A", "B"],
                "article": ["X", "X"],
                "quantite_tot": [2, 1],
            }
        )

        fig = build_fig_top_achat(df)

        assert fig.data[0].x is not None
        assert fig.data[0].y is not None