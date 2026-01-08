"""Fonctions de préparation des données pour la page *client*.

Ce module sert à :
- filtrer les clients et leurs commandes selon une sélection,
- rattacher le stock aux commandes en conservant les commandes même si aucune
  information de stock n'existe,
- préparer des colonnes utiles (prix unitaire, valeur réelle).
"""

import pandas as pd


def prepare_client_filters(
    df: pd.DataFrame,
    df_sto: pd.DataFrame,
    df_com: pd.DataFrame,
    sel_clients: list[str],
    df_art: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Filtre les DataFrames et rattache le stock aux commandes.

    Le rattachement conserve toutes les commandes (même si stock absent).

    Paramètres
    ----------
    df : pd.DataFrame
        Table clients (colonne `nom_du_client`).
    df_sto : pd.DataFrame
        Table stock (colonne `n_document`).
    df_com : pd.DataFrame
        Table commandes (colonnes `nom_du_client`, `n_document`, `date`).
    sel_clients : list[str]
        Clients sélectionnés.
    df_art : pd.DataFrame
        Table articles (colonnes `code_article`, `pv_ht`).

    Retours
    -------
    tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
        (clients_filtrés, commandes_filtrées, stock_rattaché_aux_commandes)
    """

    df_filtre = df[df["nom_du_client"].astype(str).isin(sel_clients)].copy()
    df_com_filtre = df_com[df_com["nom_du_client"].astype(str).isin(sel_clients)].copy()

    # Conserver toutes les commandes (côté droit) et ajouter le stock si dispo.
    df_stock_filtred = df_sto.merge(df_com_filtre, on="n_document", how="right")

    if "date" in df_com_filtre.columns:
        df_com_filtre["date"] = pd.to_datetime(df_com_filtre["date"], errors="coerce").dt.date

    if "date_y" in df_stock_filtred.columns:
        df_stock_filtred["date_y"] = pd.to_datetime(
            df_stock_filtred["date_y"], errors="coerce"
        ).dt.date

    df_stock_filtred = df_stock_filtred.drop(
        columns=["r_f_rence", "code_emplacement", "date_limite"],
        errors="ignore",
    )

    if ("code_article" in df_stock_filtred.columns) and ("pv_ht" in df_art.columns):
        prix_ref = df_art.set_index("code_article")["pv_ht"]
        df_stock_filtred["prix_unitaire"] = df_stock_filtred["code_article"].map(prix_ref)
    else:
        df_stock_filtred["prix_unitaire"] = pd.NA

    if "quantite_reel" in df_stock_filtred.columns:
        df_stock_filtred["valeur_reelle"] = (
            df_stock_filtred["prix_unitaire"] * df_stock_filtred["quantite_reel"]
        )
    else:
        df_stock_filtred["valeur_reelle"] = pd.NA

    return df_filtre, df_com_filtre, df_stock_filtred


def build_df_full(sql_suivi_temp_df: pd.DataFrame) -> pd.DataFrame:
    """Complète un suivi mensuel en remplissant les combinaisons manquantes à 0."""

    df = sql_suivi_temp_df.copy()

    idx = pd.MultiIndex.from_product(
        [df["nom"].unique(), df["mois_annee"].unique()],
        names=["nom", "mois_annee"],
    )

    df_full = df.set_index(["nom", "mois_annee"]).reindex(idx).reset_index()
    df_full["quantite"] = df_full["quantite"].fillna(0)

    return df_full