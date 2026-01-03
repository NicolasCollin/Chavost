from __future__ import annotations

from dataclasses import dataclass

import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st


def make_con() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(database=":memory:")


def register_tables(
    con: duckdb.DuckDBPyConnection,
    df_stock: pd.DataFrame,
    df_article: pd.DataFrame,
    df_commande: pd.DataFrame,
) -> duckdb.DuckDBPyConnection:
    con.register("stock", df_stock)
    con.register("article", df_article)
    con.register("commande", df_commande)
    return con


@dataclass(frozen=True)
class CuveFilters:
    sel_cuvees: list[str]
    sel_annees: list[int]


def prepare_cuve_filters(
    df_stock: pd.DataFrame,
    df_article: pd.DataFrame,
    df_commande: pd.DataFrame,
    sel_cuvees: list[str],
    sel_annees: list[int],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df_s = df_stock.copy()
    df_a = df_article.copy()
    df_c = df_commande.copy()

    if "date" in df_s.columns:
        df_s["date"] = pd.to_datetime(
            df_s["date"], errors="coerce"
        )  # conversion robuste

    if sel_cuvees and "article" in df_s.columns:
        df_s = df_s[df_s["article"].astype(str).isin(sel_cuvees)]

    if sel_annees and "date" in df_s.columns:
        df_s = df_s[df_s["date"].dt.year.isin(sel_annees)]

    if "article" in df_s.columns and not df_s.empty and "article" in df_a.columns:
        articles = df_s["article"].dropna().astype(str).unique().tolist()
        df_a = df_a[df_a["article"].astype(str).isin(articles)]

    return df_s, df_a, df_c


def query_kpis_produits(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    q = """
    SELECT
        COUNT(*) AS nb_mouvements,
        COUNT(DISTINCT article) AS nb_cuvees,
        SUM(ABS(quantit_)) AS quantite_vendue,
        SUM(ABS(valeur_du_mouvement)) AS valeur_ventes
    FROM stock
    WHERE quantit_ < 0
    """
    return con.execute(q).df()


def query_top_cuvees_quantite(
    con: duckdb.DuckDBPyConnection, top_n: int = 10
) -> pd.DataFrame:
    q = f"""
    SELECT
        article,
        SUM(ABS(quantit_)) AS quantite_vendue
    FROM stock
    WHERE quantit_ < 0
    GROUP BY article
    ORDER BY quantite_vendue DESC
    LIMIT {int(top_n)}
    """
    return con.execute(q).df()


def query_top_cuvees_valeur(
    con: duckdb.DuckDBPyConnection, top_n: int = 10
) -> pd.DataFrame:
    q = f"""
    SELECT
        article,
        SUM(ABS(valeur_du_mouvement)) AS valeur_ventes
    FROM stock
    WHERE quantit_ < 0
    GROUP BY article
    ORDER BY valeur_ventes DESC
    LIMIT {int(top_n)}
    """
    return con.execute(q).df()


def query_evolution_mensuelle(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    q = """
    SELECT
        STRFTIME(date, '%Y-%m') AS mois,
        SUM(ABS(quantit_)) AS quantite_vendue,
        SUM(ABS(valeur_du_mouvement)) AS valeur_ventes
    FROM stock
    WHERE quantit_ < 0
      AND date IS NOT NULL
    GROUP BY mois
    ORDER BY mois
    """
    return con.execute(q).df()


def query_abc_cuvees(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    q = """
    WITH base AS (
        SELECT
            article,
            SUM(ABS(valeur_du_mouvement)) AS valeur_ventes
        FROM stock
        WHERE quantit_ < 0
        GROUP BY article
    ),
    ranked AS (
        SELECT
            article,
            valeur_ventes,
            ROW_NUMBER() OVER (ORDER BY valeur_ventes DESC) AS rang,
            SUM(valeur_ventes) OVER () AS total_valeur,
            SUM(valeur_ventes) OVER (
                ORDER BY valeur_ventes DESC
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) AS cumul_valeur
        FROM base
    )
    SELECT
        article,
        valeur_ventes,
        rang,
        total_valeur,
        cumul_valeur,
        CASE
            WHEN total_valeur = 0 THEN 0
            ELSE cumul_valeur / total_valeur
        END AS cumul_part,
        CASE
            WHEN total_valeur = 0 THEN 'C'
            WHEN cumul_valeur / total_valeur <= 0.80 THEN 'A'
            WHEN cumul_valeur / total_valeur <= 0.95 THEN 'B'
            ELSE 'C'
        END AS classe_abc
    FROM ranked
    ORDER BY rang
    """
    return con.execute(q).df()


def query_risque_rupture(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    q = """
    WITH bornes AS (
        SELECT MAX(date) AS max_date
        FROM stock
        WHERE date IS NOT NULL
    ),
    stock_net AS (
        SELECT
            article,
            SUM(quantit_) AS stock_actuel
        FROM stock
        GROUP BY article
    ),
    ventes_30j AS (
        SELECT
            s.article,
            SUM(ABS(s.quantit_)) AS ventes_30j
        FROM stock s
        CROSS JOIN bornes b
        WHERE s.quantit_ < 0
          AND s.date IS NOT NULL
          AND b.max_date IS NOT NULL
          AND s.date >= b.max_date - INTERVAL 30 DAY
        GROUP BY s.article
    ),
    base AS (
        SELECT
            n.article,
            n.stock_actuel,
            CASE
                WHEN n.stock_actuel < 0 THEN 0
                ELSE n.stock_actuel
            END AS stock_disponible,
            COALESCE(v.ventes_30j, 0) AS ventes_30j
        FROM stock_net n
        LEFT JOIN ventes_30j v ON v.article = n.article
    )
    SELECT
        article,
        stock_actuel,
        ventes_30j,
        CASE
            WHEN ventes_30j = 0 THEN NULL
            ELSE ventes_30j / 30.0
        END AS conso_jour,
        CASE
            WHEN ventes_30j = 0 THEN NULL
            ELSE stock_disponible / (ventes_30j / 30.0)
        END AS couverture_jours,
        CASE
            WHEN stock_actuel < 0 THEN 'Stock négatif (anomalie)'
            WHEN ventes_30j = 0 THEN 'Pas de ventes récentes'
            WHEN stock_disponible / (ventes_30j / 30.0) < 7 THEN 'Risque élevé'
            WHEN stock_disponible / (ventes_30j / 30.0) < 14 THEN 'Risque modéré'
            ELSE 'Risque faible'
        END AS niveau_risque,
        CASE
            WHEN stock_actuel < 0 THEN 'Vérifier stock initial / historisation des mouvements'
            WHEN ventes_30j = 0 THEN 'Aucune consommation récente, surveiller sans urgence'
            WHEN stock_disponible / (ventes_30j / 30.0) < 7 THEN 'Réassort prioritaire / sécuriser stock'
            WHEN stock_disponible / (ventes_30j / 30.0) < 14 THEN 'Prévoir réassort prochainement'
            ELSE 'RAS'
        END AS recommandation
    FROM base
    ORDER BY
        CASE WHEN stock_actuel < 0 THEN 0 ELSE 1 END,
        CASE WHEN couverture_jours IS NULL THEN 999999 ELSE couverture_jours END ASC
    LIMIT 50
    """
    return con.execute(q).df()


def build_fig_top_cuvees(df: pd.DataFrame, value_col: str, title: str):
    if df.empty:
        return px.bar(title=title)

    d = df.sort_values(value_col, ascending=True)  # horizontal plus lisible
    fig = px.bar(
        d,
        x=value_col,
        y="article",
        orientation="h",
        title=title,
        labels={"article": "Cuvée", value_col: value_col},
    )
    return fig


def build_fig_evolution_quantite(df: pd.DataFrame):
    if df.empty:
        return px.line(title="Quantités vendues par mois")

    fig = px.line(
        df,
        x="mois",
        y="quantite_vendue",
        markers=True,
        title="Quantités vendues par mois",
        labels={"mois": "Mois", "quantite_vendue": "Quantité vendue"},
    )
    return fig


def build_fig_evolution_valeur(df: pd.DataFrame):
    if df.empty:
        return px.line(title="Valeur vendue par mois")

    fig = px.line(
        df,
        x="mois",
        y="valeur_ventes",
        markers=True,
        title="Valeur vendue par mois",
        labels={"mois": "Mois", "valeur_ventes": "Valeur vendue"},
    )
    return fig


def build_fig_pareto_abc(df: pd.DataFrame):
    if df.empty:
        return px.line(title="Pareto (cumul de la valeur)")

    fig = px.line(
        df,
        x="rang",
        y="cumul_part",
        markers=True,
        title="Pareto (cumul de la valeur vendue)",
        labels={"rang": "Rang (cuvées triées)", "cumul_part": "Part cumulée"},
    )
    fig.update_yaxes(tickformat=".0%")  # affichage en pourcentage

    fig.add_hline(y=0.80, line_dash="dot")  # seuil A
    fig.add_hline(y=0.95, line_dash="dot")  # seuil B

    return fig


def build_fig_abc_repartition(df: pd.DataFrame):
    if df.empty:
        return px.bar(title="Répartition ABC")

    rep = (
        df["classe_abc"]
        .value_counts()
        .rename_axis("classe_abc")
        .reset_index(name="nb_cuvees")
        .sort_values("classe_abc")
    )
    fig = px.bar(
        rep,
        x="classe_abc",
        y="nb_cuvees",
        title="Répartition ABC (nombre de cuvées)",
        labels={"classe_abc": "Classe", "nb_cuvees": "Nombre de cuvées"},
    )
    return fig


def render_kpis_produits(df_kpis: pd.DataFrame) -> None:
    if df_kpis.empty:
        st.info("Aucune donnée disponible pour les KPI.")
        return

    row = df_kpis.iloc[0].to_dict()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Mouvements (ventes)", int(row.get("nb_mouvements", 0)))
    c2.metric("Cuvées vendues", int(row.get("nb_cuvees", 0)))
    c3.metric("Quantité vendue", f"{float(row.get('quantite_vendue', 0.0)):,.0f}")
    c4.metric("Valeur des ventes", f"{float(row.get('valeur_ventes', 0.0)):,.0f} €")


def render_table(df: pd.DataFrame, title: str) -> None:
    st.markdown(f"### {title}")
    st.dataframe(df, use_container_width=True, hide_index=True)
