import streamlit as st

from src.utils.engineering import df_article, df_commande, df_stock

from src.interface.onglet.cuve_page.features.db import make_con, register_tables
from src.interface.onglet.cuve_page.features.prepare import prepare_cuve_filters
from src.interface.onglet.cuve_page.features.queries import (
    query_abc_cuvees,
    query_evolution_mensuelle,
    query_kpis_produits,
    query_risque_rupture,
    query_top_cuvees_quantite,
    query_top_cuvees_valeur,
)
from src.interface.onglet.cuve_page.features.render import (
    render_kpis_produits,
    render_table,
)
from src.interface.onglet.cuve_page.features.viz import (
    build_fig_abc_repartition,
    build_fig_evolution_quantite,
    build_fig_evolution_valeur,
    build_fig_pareto_abc,
    build_fig_top_cuvees,
)


def cuve_tool() -> None:
    """Affiche la page Streamlit 'Analyse des produits'."""
    con = make_con()

    df_sto = df_stock()
    df_art = df_article()
    df_com = df_commande()

    st.markdown("---")
    st.title("Analyse des produits")

    st.markdown(
        """
Cette page sert à piloter les cuvées :
- Top quantités / valeur
- Évolution mensuelle
- Pareto / ABC
- Risque de rupture (simple)
"""
    )

    st.markdown("---")

    articles_all = (
        df_sto["article"].dropna().astype(str).sort_values().unique().tolist()
        if "article" in df_sto.columns
        else []
    )

    annees_all = []
    if "date" in df_sto.columns and not df_sto.empty:
        try:
            annees_all = df_sto["date"].dt.year.dropna().sort_values().unique().tolist()
        except Exception:
            annees_all = []

    c0, c1, c2 = st.columns([2, 1, 1])

    sel_cuvees = c0.multiselect(
        "Sélectionner des cuvées (laisser vide pour tout)",
        options=articles_all,
        default=[],
    )

    sel_annees = c1.multiselect(
        "Années",
        options=annees_all,
        default=annees_all[-1:] if annees_all else [],
    )

    top_n = c2.selectbox("Top N", options=[5, 10, 15, 20], index=1)

    df_stock_f, df_article_f, df_commande_f = prepare_cuve_filters(
        df_stock=df_sto,
        df_article=df_art,
        df_commande=df_com,
        sel_cuvees=sel_cuvees,
        sel_annees=sel_annees,
    )

    con = register_tables(
        con=con,
        df_stock=df_stock_f,
        df_article=df_article_f,
        df_commande=df_commande_f,
    )

    st.markdown("## Résumé chiffré")
    with st.container(border=True):
        df_kpis = query_kpis_produits(con)
        render_kpis_produits(df_kpis)

    st.markdown("## Top cuvées")
    with st.container(border=True):
        top_q = query_top_cuvees_quantite(con, top_n=top_n)
        top_v = query_top_cuvees_valeur(con, top_n=top_n)

        cc1, cc2 = st.columns(2)

        with cc1:
            fig_top_q = build_fig_top_cuvees(
                top_q,
                value_col="quantite_vendue",
                title=f"Top {top_n} — Quantités vendues",
            )
            st.plotly_chart(fig_top_q, use_container_width=True)

        with cc2:
            fig_top_v = build_fig_top_cuvees(
                top_v,
                value_col="valeur_ventes",
                title=f"Top {top_n} — Valeur des ventes",
            )
            st.plotly_chart(fig_top_v, use_container_width=True)

        with st.expander("Afficher les tables", expanded=False):
            render_table(top_q, "Top quantités")
            render_table(top_v, "Top valeur")

    st.markdown("## Évolution mensuelle")
    with st.container(border=True):
        evol = query_evolution_mensuelle(con)

        c3, c4 = st.columns(2)

        with c3:
            fig_evol_q = build_fig_evolution_quantite(evol)
            st.plotly_chart(fig_evol_q, use_container_width=True)

        with c4:
            fig_evol_v = build_fig_evolution_valeur(evol)
            st.plotly_chart(fig_evol_v, use_container_width=True)

        with st.expander("Afficher la table", expanded=False):
            render_table(evol, "Série mensuelle")

    st.markdown("## Pareto / ABC")
    with st.container(border=True):
        abc = query_abc_cuvees(con)

        c5, c6 = st.columns([2, 1])

        with c5:
            fig_pareto = build_fig_pareto_abc(abc)
            st.plotly_chart(fig_pareto, use_container_width=True)

        with c6:
            fig_rep = build_fig_abc_repartition(abc)
            st.plotly_chart(fig_rep, use_container_width=True)

        with st.expander("Afficher la table ABC", expanded=False):
            render_table(abc, "Table ABC")

    st.markdown("## Risque de rupture (simple)")
    with st.container(border=True):
        rupt = query_risque_rupture(con)
        render_table(rupt, "Produits à surveiller")

    st.markdown("---")
    with st.expander("Voir les données filtrées (debug)", expanded=False):
        st.dataframe(df_stock_f, use_container_width=True)


if __name__ == "__main__":
    cuve_tool()
