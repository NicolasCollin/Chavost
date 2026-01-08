"""Tests unitaires (simples) de l’onglet *sales*.

Objectif :

- Vérifier que `get_and_prepare_data()` fusionne correctement les sources et
  convertit la colonne `date` au bon type ;
- Vérifier que `render_sales_page()` stocke les données dans `st.session_state`
  et réutilise le cache si présent.
"""

import pandas as pd
import pytest

import src.interface.onglet.sales as sales


class _Ctx:
    """Contexte minimal pour simuler `with st.sidebar:` et `with st.spinner():`."""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class _Col:
    """Colonne Streamlit factice (utilisée par `st.columns`)."""

    def metric(self, *args, **kwargs):
        return None

    def plotly_chart(self, *args, **kwargs):
        return None


class _DummyStreamlit:
    """Remplacement minimal de l’API Streamlit utilisée dans `sales.py`.

    Notes
    -----
    On ne cherche pas à reproduire toute l’API Streamlit : seulement les
    attributs/méthodes nécessaires au rendu de la page *sales*.
    """

    def __init__(self):
        self.session_state = {}
        self.sidebar = _Ctx()

    def title(self, *args, **kwargs):
        return None

    def header(self, *args, **kwargs):
        return None

    def date_input(self, label, value):
        return (value[0].date(), value[1].date())

    def columns(self, n):
        return tuple(_Col() for _ in range(n))

    def markdown(self, *args, **kwargs):
        return None

    def tabs(self, labels):
        return tuple(_Ctx() for _ in labels)

    def plotly_chart(self, *args, **kwargs):
        return None

    def spinner(self, *args, **kwargs):
        return _Ctx()

    def error(self, *args, **kwargs):
        return None


def test_get_and_prepare_data_merges_and_parses_date(monkeypatch):
    """`get_and_prepare_data` doit fusionner et parser correctement `date`."""

    df_mouv = pd.DataFrame(
        {
            "code_article": [1, 2],
            "n_document": ["DOC1", "DOC2"],
            "date": ["2024-01-01", "2024-01-02"],
            "valeur_du_mouvement": [10.0, 20.0],
            "quantite_reel": [1, 2],
        }
    )
    df_arts = pd.DataFrame(
        {"code_article": ["1", "2"], "libell_": ["Cuvee A", "Cuvee B"], "unit_": ["bt", "bt"]}
    )
    df_histo = pd.DataFrame(
        {
            "n_document": ["DOC1", "DOC2"],
            "code_client": ["C1", "C2"],
            "libell_famille": ["Pro", "Part"],
            "nom_du_client": ["Alice", "Bob"],
        }
    )

    monkeypatch.setattr(sales, "df_stock", lambda: df_mouv)
    monkeypatch.setattr(sales, "df_article", lambda: df_arts)
    monkeypatch.setattr(sales, "df_clients", lambda: df_histo)

    out = sales.get_and_prepare_data()

    assert "libell_" in out.columns
    assert "unit_" in out.columns
    assert "nom_du_client" in out.columns
    assert pd.api.types.is_datetime64_any_dtype(out["date"])
    assert out.loc[out["n_document"] == "DOC1", "nom_du_client"].iloc[0] == "Alice"


def test_render_sales_page_loads_data_into_session_state(monkeypatch):
    """`render_sales_page` doit écrire le DataFrame dans `st.session_state`."""

    dummy_st = _DummyStreamlit()
    monkeypatch.setattr(sales, "st", dummy_st)

    df = pd.DataFrame({"date": pd.to_datetime(["2024-01-01", "2024-01-02"])})
    monkeypatch.setattr(sales, "get_and_prepare_data", lambda: df)

    sales.render_sales_page()

    assert "sales_dashboard_data" in dummy_st.session_state
    assert isinstance(dummy_st.session_state["sales_dashboard_data"], pd.DataFrame)


def test_render_sales_page_uses_cached_session_state(monkeypatch):
    """Si le cache existe, `render_sales_page` ne doit pas recalculer les données."""

    dummy_st = _DummyStreamlit()
    dummy_st.session_state["sales_dashboard_data"] = pd.DataFrame(
        {"date": pd.to_datetime(["2024-01-01", "2024-01-02"])}
    )
    monkeypatch.setattr(sales, "st", dummy_st)

    def _boom():
        raise AssertionError("get_and_prepare_data should not be called when cached")

    monkeypatch.setattr(sales, "get_and_prepare_data", _boom)

    sales.render_sales_page()