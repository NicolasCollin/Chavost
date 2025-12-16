import pandas as pd


def prepare_client_filters(df, df_sto, df_com, sel_clients):
    """
    Reproduit ta logique :
    - df_filtre
    - df_com_filtre
    - df_stock_filtred
    """
    df_filtre = df[df["nom_du_client"].astype(str).isin(sel_clients)].copy()
    df_com_filtre = df_com[df_com["nom_du_client"].isin(sel_clients)]
    df_stock_filtred = df_com_filtre.merge(df_sto, on="n_document", how="left")
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
