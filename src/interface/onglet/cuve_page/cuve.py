import streamlit as st

from src.utils.engineering import df_article, df_commande, df_stock

from src.interface.onglet.cuve_page.features.analyse_cuve import (
    make_con,
    register_tables,
    prepare_cuve_filters,
    query_kpis_produits,
    query_top_cuvees_quantite,
    query_top_cuvees_valeur,
    query_evolution_mensuelle,
    query_abc_cuvees,
    query_risque_rupture,
    build_fig_top_cuvees,
    build_fig_evolution_quantite,
    build_fig_evolution_valeur,
    build_fig_abc,
    render_kpis_produits,
    render_table,
)


def cuve_tool() -> None:
    """
    Page Streamlit : Analyse des produits (cuvées).

    Objectif :
    - Donner une vue "entreprise" sur les cuvées : volumes, valeur, évolution, Pareto/ABC, risque de rupture.
    - Garder un code simple et facile à modifier.
    """
    con = make_con()

    df_sto = df_stock()
    df_art = df_article()
    df_com = df_commande()

    st.markdown("---")
    st.title("Analyse des produits (cuvées)")
    st.markdown(
        """
Bienvenue sur la page **Analyse des produits**.

Ici, tu peux :
- Suivre les **volumes vendus** par cuvée,
- Identifier les **tops** (quantité / valeur),
- Observer l'**évolution mensuelle**,
- Faire un **Pareto / ABC**,
- Repérer un **risque de rupture** (couverture en jours sur la base des ventes récentes).
"""
    )

    # Sélecteurs (filtres)
    articles_all = (
        df_sto["article"].dropna().astype(str).sort_values().unique().tolist()
        if "article" in df_sto.columns
        else []
    )

    annees_all = (
        df_sto["date"].dt.year.dropna().sort_values().unique().tolist()
        if ("date" in df_sto.columns and not df_sto.empty)
        else []
    )

    c0, c1, c2 = st.columns([2, 1, 1])

    sel_cuvees = c0.multiselect(
        "Sélectionner des cuvées (laisser vide pour tout)",
        options=articles_all,
        default=[],
        help="Tu peux filtrer sur quelques cuvées pour améliorer la lisibilité.",
    )

    sel_annees = c1.multiselect(
        "Années",
        options=annees_all,
        default=annees_all[-1:] if annees_all else [],
        help="Filtre temporel simple sur l'année.",
    )

    top_n = c2.selectbox("Top N", options=[5, 10, 15, 20], index=1)

    # Préparation des données filtrées + SQL
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

    # KPIs
    st.markdown("## Résumé chiffré")
    with st.container(border=True):
        sql_kpis = query_kpis_produits(con)
        render_kpis_produits(sql_kpis)

    # Tops cuvées
    st.markdown("## Top cuvées")
    with st.container(border=True):
        top_q = query_top_cuvees_quantite(con, top_n=top_n)
        top_v = query_top_cuvees_valeur(con, top_n=top_n)

        cc1, cc2 = st.columns(2)
        with cc1:
            fig_top_q = build_fig_top_cuvees(top_q, y_col="quantite_vendue", title=f"Top {top_n} — Quantités vendues")
            st.plotly_chart(fig_top_q, use_container_width=True)
        with cc2:
            fig_top_v = build_fig_top_cuvees(top_v, y_col="valeur_mouvement", title=f"Top {top_n} — Valeur des mouvements")
            st.plotly_chart(fig_top_v, use_container_width=True)

        with st.expander("Afficher les tables"):
            render_table(top_q, "Top quantités")
            render_table(top_v, "Top valeur")

    # Évolution mensuelle
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

        with st.expander("Afficher la table"):
            render_table(evol, "Série mensuelle")

    # ABC / Pareto
    st.markdown("## Pareto / ABC (sur la valeur des mouvements)")
    with st.container(border=True):
        abc = query_abc_cuvees(con)

        fig_abc = build_fig_abc(abc)
        st.plotly_chart(fig_abc, use_container_width=True)

        with st.expander("Afficher la table ABC"):
            render_table(abc, "ABC cuvées")

    # Risque de rupture (simple)
    st.markdown("## Risque de rupture (simple)")
    st.caption(
        "Heuristique : stock net (entrées - sorties) et couverture en jours basée sur les ventes des 30 derniers jours."
    )

    with st.container(border=True):
        rupt = query_risque_rupture(con)
        render_table(rupt, "Produits à surveiller")
