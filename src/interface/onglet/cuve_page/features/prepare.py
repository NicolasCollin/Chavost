from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class CuveFilters:
    """Filtres appliqués sur la page cuvées."""

    sel_cuvees: list[str]
    sel_annees: list[int]


def prepare_cuve_filters(
    df_stock: pd.DataFrame,
    df_article: pd.DataFrame,
    df_commande: pd.DataFrame,
    sel_cuvees: list[str],
    sel_annees: list[int],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Applique les filtres (cuvées / années) sur la table stock.

    Notes
    -----
    - La conversion de date est volontairement robuste (errors='coerce').
    - La table article est alignée sur les cuvées restantes.
    """
    df_s = df_stock.copy()
    df_a = df_article.copy()
    df_c = df_commande.copy()

    if "date" in df_s.columns:
        df_s["date"] = pd.to_datetime(df_s["date"], errors="coerce")  # robustesse

    if sel_cuvees and "article" in df_s.columns:
        df_s = df_s[df_s["article"].astype(str).isin(sel_cuvees)]

    if sel_annees and "date" in df_s.columns:
        df_s = df_s[df_s["date"].dt.year.isin(sel_annees)]

    if "article" in df_s.columns and not df_s.empty and "article" in df_a.columns:
        articles = df_s["article"].dropna().astype(str).unique().tolist()
        df_a = df_a[df_a["article"].astype(str).isin(articles)]

    return df_s, df_a, df_c
