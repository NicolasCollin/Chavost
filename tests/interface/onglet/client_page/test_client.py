"""Tests unitaires de `client.py` (branchement selon la sélection).

Principe
--------
Ces tests sont volontairement "miroir" : on ne teste pas Streamlit ni DuckDB.
On vérifie uniquement le routage logique :
- si aucun client n'est sélectionné : `st.info` est appelé ;
- si au moins un client est sélectionné : le pipeline (prepare -> register -> queries -> viz)
  est exécuté et les sorties (plotly + dataframe) sont demandées.

On monkeypatch toutes les dépendances (chargement de fichiers, requêtes, rendu).
"""

import pandas as pd

from src.interface.onglet.client_page import client as client_mod


class _Ctx:
    """Contexte minimal pour simuler `with st.expander(...)` et `with st.container(...)`."""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class TestClientTool:
    """Tests des deux comportements principaux de `client_tool`."""

    def test_aucune_selection_affiche_info(self, monkeypatch) -> None:
        """Vérifie que `st.info` est appelé lorsque la sélection est vide."""

        info_calls: list[None] = []

        monkeypatch.setattr(client_mod, "make_con", lambda: object())
        monkeypatch.setattr(client_mod, "df_clients", lambda: pd.DataFrame({"nom_du_client": ["A"]}))
        monkeypatch.setattr(client_mod, "df_stock", lambda: pd.DataFrame())
        monkeypatch.setattr(client_mod, "df_commande", lambda: pd.DataFrame())
        monkeypatch.setattr(client_mod, "df_article", lambda: pd.DataFrame())
        monkeypatch.setattr(client_mod, "df_info_client", lambda: pd.DataFrame())

        monkeypatch.setattr(client_mod.st, "markdown", lambda *_a, **_k: None)
        monkeypatch.setattr(client_mod.st, "title", lambda *_a, **_k: None)
        monkeypatch.setattr(client_mod.st, "multiselect", lambda *_a, **_k: [])
        monkeypatch.setattr(client_mod.st, "info", lambda *_a, **_k: info_calls.append(None))

        client_mod.client_tool()

        assert len(info_calls) == 1

    def test_selection_declenche_les_appels_et_affichages(self, monkeypatch) -> None:
        """Vérifie que le pipeline est exécuté lorsqu'au moins un client est sélectionné."""

        render_kpis_calls: list[None] = []
        render_info_calls: list[None] = []
        plotly_calls: list[None] = []
        dataframe_calls: list[None] = []

        con = object()

        # Données minimales
        df_clients = pd.DataFrame({"nom_du_client": ["A", "B"], "info": [1, 2]})
        df_com = pd.DataFrame(
            {
                "nom_du_client": ["A"],
                "n_document": ["FA001"],
                "date": pd.to_datetime(["2025-01-10"]),
                "net_payer": [10.0],
            }
        )
        df_sto = pd.DataFrame(
            {
                "nom_du_client": ["A"],
                "n_document": ["FA001"],
                "article": ["X"],
                "quantit_": [-1],
                "date": pd.to_datetime(["2025-01-10"]),
            }
        )
        df_art = pd.DataFrame({"code_article": ["X"], "pv_ht": [12.0]})
        df_info = pd.DataFrame({"email": ["a@a.fr", "b@b.fr"], "unname_tmp": [1, 2]})

        # Chargements
        monkeypatch.setattr(client_mod, "make_con", lambda: con)
        monkeypatch.setattr(client_mod, "df_clients", lambda: df_clients)
        monkeypatch.setattr(client_mod, "df_stock", lambda: df_sto)
        monkeypatch.setattr(client_mod, "df_commande", lambda: df_com)
        monkeypatch.setattr(client_mod, "df_article", lambda: df_art)
        monkeypatch.setattr(client_mod, "df_info_client", lambda: df_info)

        # Streamlit UI
        monkeypatch.setattr(client_mod.st, "markdown", lambda *_a, **_k: None)
        monkeypatch.setattr(client_mod.st, "title", lambda *_a, **_k: None)
        monkeypatch.setattr(client_mod.st, "write", lambda *_a, **_k: None)
        monkeypatch.setattr(client_mod.st, "info", lambda *_a, **_k: None)
        monkeypatch.setattr(client_mod.st, "expander", lambda *_a, **_k: _Ctx())
        monkeypatch.setattr(client_mod.st, "container", lambda *_a, **_k: _Ctx())
        monkeypatch.setattr(client_mod.st, "columns", lambda *_a, **_k: (object(), object(), object(), object()))
        monkeypatch.setattr(client_mod.st, "plotly_chart", lambda *_a, **_k: plotly_calls.append(None))
        monkeypatch.setattr(client_mod.st, "dataframe", lambda *_a, **_k: dataframe_calls.append(None))

        # Important: éviter le bloc "Reherche des commandes par dates" (qui s'active si len(sel_clients)==1)
        monkeypatch.setattr(client_mod.st, "multiselect", lambda *_a, **_k: ["A", "B"])

        # Préparation + DB
        monkeypatch.setattr(client_mod, "prepare_client_filters", lambda *_a, **_k: (df_clients, df_com, df_sto))
        monkeypatch.setattr(client_mod, "register_tables", lambda _con, *_a, **_k: _con)

        # Requêtes (retours minimaux)
        monkeypatch.setattr(client_mod, "query_nb_commande", lambda _con: pd.DataFrame({"nb_comm": [1], "nom": ["A"]}))
        monkeypatch.setattr(client_mod, "query_tot_paye", lambda _con: pd.DataFrame({"tot_paye": [10.0], "nom": ["A"]}))
        monkeypatch.setattr(client_mod, "query_produit_distincs", lambda _con: pd.DataFrame({"prod_diff": [1], "nom": ["A"]}))
        monkeypatch.setattr(client_mod, "query_nb_tot_prod", lambda _con: pd.DataFrame({"nombre_produits": [1], "nom": ["A"]}))
        monkeypatch.setattr(
            client_mod,
            "query_suivi_temp",
            lambda _con: pd.DataFrame(
                {
                    "nom": ["A"],
                    "quantite": [1],
                    "date": pd.to_datetime(["2025-01-01"]),
                    "mois_annee": ["2025-01"],
                }
            ),
        )
        monkeypatch.setattr(client_mod, "query_suivi_temp_year", lambda _con: pd.DataFrame({"nom": ["A"], "quantite": [1], "annee": [2025]}))
        monkeypatch.setattr(client_mod, "query_top_achat", lambda _con: pd.DataFrame({"article": ["X"], "quantite_tot": [1], "nom": ["A"]}))

        # Viz
        monkeypatch.setattr(client_mod, "build_fig_suivi", lambda _df: object())
        monkeypatch.setattr(client_mod, "build_fig_suivi_year", lambda _df: object())
        monkeypatch.setattr(client_mod, "build_fig_top_achat", lambda _df: object())

        # Render
        monkeypatch.setattr(client_mod, "render_kpis", lambda *_a, **_k: render_kpis_calls.append(None))
        monkeypatch.setattr(client_mod, "render_info_client", lambda *_a, **_k: render_info_calls.append(None))
        monkeypatch.setattr(client_mod, "metric_table_date", lambda *_a, **_k: None)
        monkeypatch.setattr(client_mod, "render_affichage_commande", lambda *_a, **_k: None)

        client_mod.client_tool()

        assert len(render_info_calls) == 1
        assert len(render_kpis_calls) == 1
        assert len(plotly_calls) >= 3  # suivi + suivi_year + top
        assert len(dataframe_calls) == 1
