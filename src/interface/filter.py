import pandas as pd
import streamlit as st 

from src.utils.engineering import df_article, df_commande, df_clients, df_stock, df_client_prosp


def build_filters():
    df = df_commande()
    df_s = df_stock()
    """Render filters and return filtered dataframe + options (multi-product)."""
    with st.expander("🎛️ Filtres", expanded=True):
        # --- FILTRE TEMPOREL (slider) ---
        date_min = df["date"].min().date()
        date_max = df["date"].max().date()

        date_range = st.slider(
            "Période d'étude",
            min_value=date_min,
            max_value=date_max,
            value=(date_min, date_max),
            format="DD/MM/YYYY",
        )
        
        
        years_all = [
            y for y in df["annee"].dropna().astype(int).sort_values().unique().tolist()
        ]
        years_all_str = [str(y) for y in years_all]
        sel_years = st.multiselect("Années", years_all_str, default=years_all_str)

        types_all = sorted(df["type_produit"].dropna().unique().tolist())
        sel_types = st.multiselect("Types de produit", types_all, default=types_all)

        # --- Sélection multiple de produits (saisie assistée intégrée) ---
        prod_all = sorted(df["nom_produit"].dropna().astype(str).unique().tolist())
        sel_products = st.multiselect(
            "Produits (sélection multiple)",
            options=prod_all,
            default=[],
            help="Tapez pour filtrer et sélectionnez un ou plusieurs produits. Laissez vide pour tous.",
        )

        top_n = st.slider("Top N produits", 3, 30, 10, step=1)

    mask = df["annee_str"].isin(sel_years) & df["type_produit"].isin(sel_types)
    if sel_products:
        mask &= df["nom_produit"].isin(sel_products)

    fdf = df.loc[mask].copy()
    if fdf.empty:
        st.warning("Aucune ligne avec ces filtres.")
        st.stop()
    return fdf, top_n

