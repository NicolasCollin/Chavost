import pandas as pd
import streamlit as st


def render_kpis_produits(df_kpis: pd.DataFrame) -> None:
    """Affiche 4 KPI en haut de page."""
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
    """Affiche un tableau Streamlit."""
    st.markdown(f"### {title}")
    st.dataframe(df, use_container_width=True, hide_index=True)
