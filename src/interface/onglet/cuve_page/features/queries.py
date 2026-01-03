import duckdb
import pandas as pd


def query_kpis_produits(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """
    KPI globaux des ventes.

    Convention
    ----------
    Une vente = sortie de stock (quantit_ < 0).
    """
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
    """Top N des cuvées par quantité vendue."""
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
    """Top N des cuvées par valeur vendue."""
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
    """Série mensuelle (quantité + valeur) basée sur les ventes."""
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
    """
    Table ABC basée sur la valeur vendue.

    Classes
    -------
    A : 0–80% ; B : 80–95% ; C : 95–100%
    """
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
    """
    Estimation simple du risque de rupture.

    Principe
    --------
    - stock_actuel = somme des mouvements
    - conso_jour = ventes_30j / 30
    - couverture_jours = stock_disponible / conso_jour
    """
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
