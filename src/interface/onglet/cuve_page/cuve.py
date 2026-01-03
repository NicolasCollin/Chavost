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
    build_fig_pareto_abc,
    build_fig_abc_repartition,
    render_kpis_produits,
    render_table,
)


def cuve_tool() -> None:
    con = make_con()

    df_sto = df_stock()
    df_art = df_article()
    df_com = df_commande()

    st.markdown("---")
    st.title("Analyse des produits")

    st.markdown(
        """
Cette page sert à piloter les cuvées comme une entreprise :
- identifier les cuvées qui pèsent le plus (Top / Pareto / ABC),
- suivre l’évolution des ventes dans le temps,
- repérer les risques de rupture (couverture en jours).
"""
    )

    st.markdown("---")

    # Filtres
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
        help="Filtrer permet de rendre les graphiques plus lisibles.",
    )

    sel_annees = c1.multiselect(
        "Années",
        options=annees_all,
        default=annees_all[-1:] if annees_all else [],
        help="Filtre simple sur l'année.",
    )

    top_n = c2.selectbox("Top N", options=[5, 10, 15, 20], index=1)

    # Préparation données + SQL
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
        with st.expander("Comment lire ces KPI ?", expanded=False):
            st.markdown(
                """
- **Mouvements (ventes)** : nombre de lignes de sorties de stock (on considère une vente comme une sortie).
- **Cuvées vendues** : nombre de cuvées distinctes vendues sur la période filtrée.
- **Quantité vendue** : somme des quantités sorties.
- **Valeur des ventes** : somme des valeurs associées aux sorties.
"""
            )

    # Top cuvées
    st.markdown("## Top cuvées")
    with st.container(border=True):
        top_q = query_top_cuvees_quantite(con, top_n=top_n)
        top_v = query_top_cuvees_valeur(con, top_n=top_n)

        cc1, cc2 = st.columns(2)

        with cc1:
            st.markdown("### Quantités vendues")
            fig_top_q = build_fig_top_cuvees(
                top_q,
                value_col="quantite_vendue",
                title=f"Top {top_n} cuvées par quantité vendue",
            )
            st.plotly_chart(fig_top_q, use_container_width=True)

        with cc2:
            st.markdown("### Valeur des ventes")
            fig_top_v = build_fig_top_cuvees(
                top_v,
                value_col="valeur_ventes",
                title=f"Top {top_n} cuvées par valeur des ventes",
            )
            st.plotly_chart(fig_top_v, use_container_width=True)

        with st.expander("Afficher les tables", expanded=False):
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

        with st.expander("Comment lire ces courbes ?", expanded=False):
            st.markdown(
                """
- La courbe **quantités** montre le volume vendu par mois.
- La courbe **valeur** montre la valeur vendue par mois.
- L’idée : repérer une saisonnalité, des mois faibles/forts, ou une rupture de tendance.
"""
            )

        with st.expander("Afficher la table", expanded=False):
            render_table(evol, "Série mensuelle")

    # Pareto / ABC
    st.markdown("## Pareto / ABC (priorisation des cuvées)")
    st.caption(
        "Objectif : prioriser les cuvées qui comptent le plus dans la valeur des ventes."
    )

    with st.container(border=True):
        abc = query_abc_cuvees(con)

        c5, c6 = st.columns([2, 1])

        with c5:
            fig_pareto = build_fig_pareto_abc(abc)
            st.plotly_chart(fig_pareto, use_container_width=True)

        with c6:
            fig_rep = build_fig_abc_repartition(abc)
            st.plotly_chart(fig_rep, use_container_width=True)

        with st.expander("Comment lire Pareto / ABC ?", expanded=False):
            st.markdown(
                """
- On trie les cuvées de la plus contributrice à la moins contributrice (rang 1, rang 2, etc.).
- La courbe affiche la **part cumulée** de la valeur vendue.
- Les classes :
  - **A** : cuvées “vitales” (en général ≈ 80% de la valeur avec peu de références).
  - **B** : importantes mais secondaires (jusqu’à ≈ 95%).
  - **C** : longue traîne (beaucoup de références, faible poids).
- Utilisation :
  - **A** : stock de sécurité + suivi prioritaire,
  - **B** : suivi normal,
  - **C** : optimisation / déstockage / réduction des références.
"""
            )

        with st.expander("Afficher la table ABC", expanded=False):
            render_table(abc, "Table ABC (triée)")

    # Risque de rupture
    st.markdown("## Risque de rupture (simple)")
    st.caption(
        "Stock net (entrées - sorties) + couverture en jours basée sur les ventes des 30 derniers jours."
    )

    with st.container(border=True):
        rupt = query_risque_rupture(con)
        render_table(rupt, "Produits à surveiller")

        with st.expander("Comment c’est calculé ?", expanded=False):
            st.markdown(
                """
- **stock_actuel** = somme des mouvements (entrées - sorties).
- **ventes_30j** = volume vendu sur les 30 derniers jours (sorties).
- **conso_jour** = ventes_30j / 30.
- **couverture_jours** = stock_disponible / conso_jour (stock_disponible = max(stock_actuel, 0)).

Important :
- Si **stock_actuel est négatif**, c’est une anomalie (il manque une partie de l’historique / stock initial), on l’affiche comme alerte.
- Si **ventes_30j = 0**, la couverture est non calculable (pas de conso récente).
"""
            )

    st.markdown("---")
    with st.expander("Voir les données filtrées (debug)", expanded=False):
        st.dataframe(df_stock_f, use_container_width=True)


if __name__ == "__main__":
    cuve_tool()
