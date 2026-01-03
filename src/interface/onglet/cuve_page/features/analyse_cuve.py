from dataclasses import dataclass

import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px


# Base SQL (DuckDB)
def make_con() -> duckdb.DuckDBPyConnection:
    """
    Crée une connexion DuckDB en mémoire.

    Retour
    ------
    duckdb.DuckDBPyConnection
        Connexion en mémoire, adaptée aux analyses rapides (groupby SQL, filtres, etc.).
    """
    return duckdb.connect(database=":memory:")


def register_tables(
    con: duckdb.DuckDBPyConnection,
    df_stock: pd.DataFrame,
    df_article: pd.DataFrame,
    df_commande: pd.DataFrame,
) -> duckdb.DuckDBPyConnection:
    """
    Enregistre les DataFrames dans DuckDB comme tables.

    Tables créées :
    - stock
    - article
    - commande

    Notes
    -----
    On garde des noms simples pour écrire des requêtes lisibles.
    """
    con.register("stock", df_stock)
    con.register("article", df_article)
    con.register("commande", df_commande)
    return con


# Préparation / filtres
@dataclass(frozen=True)
class CuveFilters:
    """Petite structure pour centraliser les filtres."""
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
    Applique des filtres simples et robustes pour la page cuvées.

    Paramètres
    ----------
    df_stock : pd.DataFrame
        Table des mouvements de stock.
    df_article : pd.DataFrame
        Table articles.
    df_commande : pd.DataFrame
        Table commandes (utile si tu veux enrichir plus tard).
    sel_cuvees : list[str]
        Liste de cuvées sélectionnées (vide = toutes).
    sel_annees : list[int]
        Liste d'années (vide = toutes).

    Retour
    ------
    tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
        (df_stock_filtré, df_article_filtré, df_commande_filtré)
    """
    df_s = df_stock.copy()
    df_a = df_article.copy()
    df_c = df_commande.copy()

    if "date" in df_s.columns:
        df_s["date"] = pd.to_datetime(df_s["date"], errors="coerce")

    if sel_cuvees and "article" in df_s.columns:
        df_s = df_s[df_s["article"].astype(str).isin(sel_cuvees)]

    if sel_annees and "date" in df_s.columns:
        df_s = df_s[df_s["date"].dt.year.isin(sel_annees)]

    # Filtre article en cohérence avec stock filtré
    if "article" in df_s.columns and not df_s.empty:
        articles = df_s["article"].dropna().astype(str).unique().tolist()
        if "article" in df_a.columns:
            df_a = df_a[df_a["article"].astype(str).isin(articles)]

    # Commandes : pour l'instant on ne relie pas (pas nécessaire à l'analyse stock-based)
    return df_s, df_a, df_c



# Requêtes SQL
def query_kpis_produits(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """
    KPIs globaux sur les ventes (basées sur les sorties de stock).

    Convention :
    - On considère "vente" = mouvement avec quantit_ < 0 (sortie).
    - quantite_vendue = somme(abs(quantit_))
    - valeur_mouvement = somme(abs(valeur_du_mouvement))

    Retour
    ------
    pd.DataFrame
        Une ligne avec des KPIs.
    """
    q = """
    SELECT
        COUNT(*) AS nb_mouvements,
        COUNT(DISTINCT article) AS nb_cuvees,
        SUM(ABS(quantit_)) AS quantite_vendue,
        SUM(ABS(valeur_du_mouvement)) AS valeur_mouvement
    FROM stock
    WHERE quantit_ < 0
    """
    return con.execute(q).df()


def query_top_cuvees_quantite(con: duckdb.DuckDBPyConnection, top_n: int = 10) -> pd.DataFrame:
    """Top cuvées par quantité vendue (sorties de stock)."""
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


def query_top_cuvees_valeur(con: duckdb.DuckDBPyConnection, top_n: int = 10) -> pd.DataFrame:
    """Top cuvées par valeur des mouvements (sorties de stock)."""
    q = f"""
    SELECT
        article,
        SUM(ABS(valeur_du_mouvement)) AS valeur_mouvement
    FROM stock
    WHERE quantit_ < 0
    GROUP BY article
    ORDER BY valeur_mouvement DESC
    LIMIT {int(top_n)}
    """
    return con.execute(q).df()


def query_evolution_mensuelle(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """
    Série mensuelle (quantité vendue + valeur des mouvements).

    Retour
    ------
    pd.DataFrame
        Colonnes : mois, quantite_vendue, valeur_mouvement
    """
    q = """
    SELECT
        STRFTIME(date, '%Y-%m') AS mois,
        SUM(ABS(quantit_)) AS quantite_vendue,
        SUM(ABS(valeur_du_mouvement)) AS valeur_mouvement
    FROM stock
    WHERE quantit_ < 0
      AND date IS NOT NULL
    GROUP BY mois
    ORDER BY mois
    """
    return con.execute(q).df()


def query_abc_cuvees(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """
    Classement ABC simple basé sur la valeur des mouvements.

    Règles :
    - A : cumul <= 80%
    - B : 80% < cumul <= 95%
    - C : > 95%
    """
    q = """
    WITH base AS (
        SELECT
            article,
            SUM(ABS(valeur_du_mouvement)) AS valeur_mouvement
        FROM stock
        WHERE quantit_ < 0
        GROUP BY article
    ),
    ranked AS (
        SELECT
            article,
            valeur_mouvement,
            ROW_NUMBER() OVER (ORDER BY valeur_mouvement DESC) AS rang,
            SUM(valeur_mouvement) OVER () AS total_valeur,
            SUM(valeur_mouvement) OVER (
                ORDER BY valeur_mouvement DESC
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) AS cumul_valeur
        FROM base
    )
    SELECT
        article,
        valeur_mouvement,
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
    """
    Détection simple de produits à risque de rupture.

    Idée :
    - stock_actuel = SUM(quantit_) (entrées - sorties)
    - ventes_30j = SUM(abs(quantit_)) sur les 30 derniers jours (sorties)
    - conso_jour = ventes_30j / 30
    - couverture_jours = stock_actuel / conso_jour

    Retour
    ------
    pd.DataFrame
        Produits triés par couverture (les plus faibles en premier).
    """
    q = """
    WITH bornes AS (
        SELECT
            MAX(date) AS max_date
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
          AND s.date >= b.max_date - INTERVAL 30 DAY
        GROUP BY s.article
    )
    SELECT
        n.article,
        n.stock_actuel,
        COALESCE(v.ventes_30j, 0) AS ventes_30j,
        CASE
            WHEN COALESCE(v.ventes_30j, 0) = 0 THEN NULL
            ELSE (COALESCE(v.ventes_30j, 0) / 30.0)
        END AS conso_jour,
        CASE
            WHEN COALESCE(v.ventes_30j, 0) = 0 THEN NULL
            WHEN (COALESCE(v.ventes_30j, 0) / 30.0) = 0 THEN NULL
            ELSE n.stock_actuel / (COALESCE(v.ventes_30j, 0) / 30.0)
        END AS couverture_jours
    FROM stock_net n
    LEFT JOIN ventes_30j v ON v.article = n.article
    ORDER BY
        CASE WHEN couverture_jours IS NULL THEN 999999 ELSE couverture_jours END ASC
    LIMIT 50
    """
    return con.execute(q).df()



# Visualisations Plotly
def build_fig_top_cuvees(df: pd.DataFrame, y_col: str, title: str):
    """Bar chart simple pour un top cuvées."""
    if df.empty:
        return px.bar(title=title)
    return px.bar(df, x="article", y=y_col, title=title)


def build_fig_evolution_quantite(df: pd.DataFrame):
    """Courbe mensuelle des quantités vendues."""
    if df.empty:
        return px.line(title="Quantités vendues par mois")
    return px.line(df, x="mois", y="quantite_vendue", markers=True, title="Quantités vendues par mois")


def build_fig_evolution_valeur(df: pd.DataFrame):
    """Courbe mensuelle de la valeur des mouvements."""
    if df.empty:
        return px.line(title="Valeur des mouvements par mois")
    return px.line(df, x="mois", y="valeur_mouvement", markers=True, title="Valeur des mouvements par mois")


def build_fig_abc(df: pd.DataFrame):
    """
    Graphique simple : cumul (Pareto) + repère ABC.

    On trace la part cumulée (cumul_part) par rang.
    """
    if df.empty:
        return px.line(title="Pareto / ABC")
    return px.line(df, x="rang", y="cumul_part", markers=True, title="Pareto (cumul de la valeur)")



# Rendu Streamlit
def render_kpis_produits(df_kpis: pd.DataFrame) -> None:
    """Affiche les KPIs globaux sous forme de metrics."""
    if df_kpis.empty:
        st.info("Aucune donnée disponible pour les KPIs.")
        return

    row = df_kpis.iloc[0].to_dict()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Mouvements (ventes)", int(row.get("nb_mouvements", 0)))
    c2.metric("Cuvées vendues", int(row.get("nb_cuvees", 0)))
    c3.metric("Quantité vendue", f"{float(row.get('quantite_vendue', 0.0)):,.0f}")
    c4.metric("Valeur mouvements", f"{float(row.get('valeur_mouvement', 0.0)):,.0f} €")


def render_table(df: pd.DataFrame, title: str) -> None:
    """Affiche une table Streamlit propre."""
    st.markdown(f"### {title}")
    st.dataframe(df, use_container_width=True, hide_index=True)
