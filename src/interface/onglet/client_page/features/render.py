import streamlit as st
from src.interface.onglet.client_page.features.viz import build_fig_commande


def render_kpis(
    sel_clients,
    c1,
    c2,
    c3,
    c4,
    sql_nb_commande_df,
    sql_tot_paye_df,
    sql_produit_distincs_df,
    sql_nb_tot_prod_df,
):
    if len(sel_clients) >= 2:
        with c1:
            st.write("Nombre de commandes passées")
            st.dataframe(sql_nb_commande_df, hide_index=True)
        with c2:
            st.write("Total payé par les clients (en €)")
            st.dataframe(sql_tot_paye_df, hide_index=True)
        with c3:
            st.write("Nombre de produits différents")
            st.dataframe(sql_produit_distincs_df, hide_index=True)
        with c4:
            st.write("Nombre total de produit achaté")
            st.dataframe(sql_nb_tot_prod_df, hide_index=True)

    else:
        with c1:
            val = int(sql_nb_commande_df["nb_comm"].iloc[0])
            c1.metric("Nombre de commandes passées par le client", val)

        with c2:
            val = float(sql_tot_paye_df["tot_paye"].iloc[0])
            c2.metric("Total payé par le client (en €)", val.__format__(",.2f"))

        with c3:
            val = int(sql_produit_distincs_df["prod_diff"].iloc[0])
            c3.metric("Nombre de produits distincts achetés", val)

        with c4:
            val = float(sql_nb_tot_prod_df["nombre_produits"].iloc[0])
            c4.metric("Nombre total de produit achaté", val)


def metric_table_date(df_com_filtre, sel_date, df_order_client_by_dates):
    df_filtre_fa_ndoc = df_com_filtre[df_com_filtre["n_document"].str.startswith("FA")]
    n_doc_liste = df_filtre_fa_ndoc["n_document"].unique().tolist()
    df_doc_liste = df_filtre_fa_ndoc[df_filtre_fa_ndoc["n_document"].isin(n_doc_liste)]
    if len(sel_date) == 1:
        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Valeurs produits",
            f"""{df_order_client_by_dates['valeur_reelle']
                .sum():,.2f}€
                """,
        )
        c2.metric(
            "Nomrbre de bouteilles",
            f"""{int(-df_order_client_by_dates['quantit_']
                .sum())}
                """,
        )
        c3.metric(
            "Produits distincts",
            f"""{len(df_order_client_by_dates['article']
                .unique().tolist())}
                """,
        )
        c4.metric(
            "Prix total",
            f"""{df_doc_liste['net_payer'].sum():,.2f}€
                """,
        )
    else:
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric(
            "Total des commandes",
            f"""{df_order_client_by_dates['valeur_reelle']
                .sum():,.2f}€
                """,
        )
        c2.metric(
            "Nomrbre de bouteilles",
            f"""{-df_order_client_by_dates['quantit_']
                .sum():,.2f}
                """,
        )
        c3.metric(
            "Produits distincts",
            f"""{len(df_order_client_by_dates['article']
                .unique().tolist()):,.2f}
                """,
        )
        c4.metric(
            "Nombre de commandes",
            f"""{len(df_order_client_by_dates['date_y']
                .unique().tolist()):,.2f}
                """,
        )
        c5.metric(
            "Prix total",
            f"""{df_doc_liste['net_payer'].sum():,.2f}€
                """,
        )


def render_affichage_commande(df_order_client_by_dates):
    q1, q2 = st.columns(2)
    df_use = df_order_client_by_dates[
        ["article", "quantite_reel", "prix_unitaire", "n_document"]
    ]
    df_use["article_short"] = df_use["article"].str.slice(0, 7) + "…"
    with q1:
        st.markdown("#### Tableau récapitulatif de la commande")
        st.dataframe(df_use.drop(columns=["article_short"]), hide_index=True)
    with q2:
        fig_commande = build_fig_commande(df_use)
        st.plotly_chart(fig_commande, use_container_width=True)
