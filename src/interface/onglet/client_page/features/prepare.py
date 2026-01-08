import pandas as pd


def prepare_client_filters(df, df_sto, df_com, sel_clients, df_art):
    """
    Repro
    """
    df_filtre = df[df["nom_du_client"].astype(str).isin(sel_clients)].copy()
    df_com_filtre = df_com[df_com["nom_du_client"].isin(sel_clients)]
    df_stock_filtred = df_sto.merge(df_com_filtre, on="n_document", how="left")

    df_com_filtre["date"] = df_com_filtre["date"].dt.date
    df_stock_filtred["date_y"] = df_stock_filtred["date_y"].dt.date

    df_stock_filtred = df_stock_filtred.drop(
        columns=["r_f_rence", "code_emplacement", "date_limite"]
    ).dropna()

    # actualisation des prix unitaires
    prix_ref = df_art.set_index("code_article")["pv_ht"]
    df_stock_filtred = df_stock_filtred
    df_stock_filtred["prix_unitaire"] = df_stock_filtred["code_article"].map(prix_ref)

    df_stock_filtred["valeur_reelle"] = (
        df_stock_filtred["prix_unitaire"] * df_stock_filtred["quantite_reel"]
    )

    return df_filtre, df_com_filtre, df_stock_filtred


def build_df_full(sql_suivi_temp_df):
    """
    Reproduit exactement :
    - df = sql_suivi_temp_df.copy()
    - MultiIndex produit
    - reindex + reset_index
    - fillna(0) sur quantite
    """
    df = sql_suivi_temp_df.copy()

    idx = pd.MultiIndex.from_product(
        [df["nom"].unique(), df["mois_annee"].unique()], names=["nom", "mois_annee"]
    )

    df_full = df.set_index(["nom", "mois_annee"]).reindex(idx).reset_index()
    df_full["quantite"] = df_full["quantite"].fillna(0)

    return df_full
