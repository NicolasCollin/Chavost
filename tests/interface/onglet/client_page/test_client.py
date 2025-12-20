"""
Tests unitaires de client.py (branchement selon la sélection).

Ces tests vérifient :
- si aucun client n'est sélectionné : un message d'information est affiché
- si un client est sélectionné : les fonctions principales sont appelées et les sorties sont produites
"""

import pandas as pd

from src.interface.onglet.client_page import client as client_mod


class TestClientTool:
    """Tests des deux comportements principaux de client_tool."""

    def test_aucune_selection_affiche_info(self, monkeypatch) -> None:
        """Vérifie que st.info est appelé lorsque la sélection est vide."""
        info_calls: list[None] = []

        monkeypatch.setattr(client_mod, "make_con", lambda: object())
        monkeypatch.setattr(
            client_mod, "df_clients", lambda: pd.DataFrame({"nom_du_client": ["A"]})
        )
        monkeypatch.setattr(client_mod, "df_stock", lambda: pd.DataFrame())
        monkeypatch.setattr(client_mod, "df_commande", lambda: pd.DataFrame())

        monkeypatch.setattr(client_mod.st, "markdown", lambda *_a, **_k: None)
        monkeypatch.setattr(client_mod.st, "title", lambda *_a, **_k: None)
        monkeypatch.setattr(client_mod.st, "multiselect", lambda *_a, **_k: [])
        monkeypatch.setattr(
            client_mod.st, "info", lambda *_a, **_k: info_calls.append(None)
        )

        client_mod.client_tool()

        assert len(info_calls) == 1

    def test_selection_declenche_les_appels_et_affichages(self, monkeypatch) -> None:
        """Vérifie que les appels et affichages attendus sont déclenchés lorsqu'un client est sélectionné."""
        render_calls: list[None] = []
        plotly_calls: list[None] = []
        dataframe_calls: list[None] = []

        con = object()
        df_clients = pd.DataFrame({"nom_du_client": ["A", "B"], "info": [1, 2]})
        df_com = pd.DataFrame(
            {"nom_du_client": ["A"], "n_document": [1], "net_payer": [10.0]}
        )
        df_sto = pd.DataFrame(
            {
                "n_document": [1],
                "article": ["X"],
                "quantit_": [-1],
                "mois_annee": ["2025-01"],
            }
        )

        monkeypatch.setattr(client_mod, "make_con", lambda: con)
        monkeypatch.setattr(client_mod, "df_clients", lambda: df_clients)
        monkeypatch.setattr(client_mod, "df_stock", lambda: df_sto)
        monkeypatch.setattr(client_mod, "df_commande", lambda: df_com)

        monkeypatch.setattr(client_mod.st, "markdown", lambda *_a, **_k: None)
        monkeypatch.setattr(client_mod.st, "title", lambda *_a, **_k: None)
        monkeypatch.setattr(client_mod.st, "write", lambda *_a, **_k: None)
        monkeypatch.setattr(
            client_mod.st,
            "columns",
            lambda *_a, **_k: (object(), object(), object(), object()),
        )
        monkeypatch.setattr(client_mod.st, "multiselect", lambda *_a, **_k: ["A"])
        monkeypatch.setattr(
            client_mod.st, "plotly_chart", lambda *_a, **_k: plotly_calls.append(None)
        )
        monkeypatch.setattr(
            client_mod.st, "dataframe", lambda *_a, **_k: dataframe_calls.append(None)
        )

        monkeypatch.setattr(
            client_mod,
            "prepare_client_filters",
            lambda *_a, **_k: (df_clients.head(1), df_com, df_sto),
        )
        monkeypatch.setattr(client_mod, "register_tables", lambda _con, *_a, **_k: _con)

        monkeypatch.setattr(
            client_mod,
            "query_nb_commande",
            lambda _con: pd.DataFrame({"nb_comm": [1], "nom": ["A"]}),
        )
        monkeypatch.setattr(
            client_mod,
            "query_tot_paye",
            lambda _con: pd.DataFrame({"tot_paye": [10.0], "nom": ["A"]}),
        )
        monkeypatch.setattr(
            client_mod,
            "query_produit_distincs",
            lambda _con: pd.DataFrame({"prod_diff": [1], "nom": ["A"]}),
        )
        monkeypatch.setattr(
            client_mod,
            "query_nb_tot_prod",
            lambda _con: pd.DataFrame({"nombre_produits": [1], "nom": ["A"]}),
        )
        monkeypatch.setattr(
            client_mod,
            "query_suivi_temp",
            lambda _con: pd.DataFrame(
                {"nom": ["A"], "quantite": [1], "mois_annee": ["2025-01"]}
            ),
        )
        monkeypatch.setattr(
            client_mod,
            "query_top_achat",
            lambda _con: pd.DataFrame(
                {"article": ["X"], "quantite_tot": [1], "nom": ["A"]}
            ),
        )

        monkeypatch.setattr(client_mod, "build_df_full", lambda df: df)
        monkeypatch.setattr(client_mod, "build_fig_suivi", lambda _df: object())
        monkeypatch.setattr(client_mod, "build_fig_top_achat", lambda _df: object())
        monkeypatch.setattr(
            client_mod, "render_kpis", lambda *_a, **_k: render_calls.append(None)
        )

        client_mod.client_tool()

        assert len(render_calls) == 1
        assert len(plotly_calls) == 2
        assert len(dataframe_calls) == 1
