import streamlit as st
import pandas as pd

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


def show_metric_if_exists(col, val, name_val):
    if pd.isna(val):
        col.metric(name_val, "")
        col.info("Cette valeur n'est pas connue")
    else:
        col.metric(name_val, val)


def render_info_client(df_info_cli, sel_clients):
    if len(sel_clients) > 1:
        client = st.selectbox(
            "Sur quel clients voulez vous des informations personelles", sel_clients
        )
    else:
        client = sel_clients[0]
        # df_info_filtre = df_info_cli[df_info_cli]

    # Dataframe des informations du client
    df_filtre_client = df_info_cli[df_info_cli["nom_client"] == client]
    if df_filtre_client.empty:
        st.warning("⚠️ Ce client n'est pas référencé dans les données clients")
    else:
        # ----On écrit alors les informations----

        # Deux premières colonnes
        i1, i2 = st.columns(2)

        # LE nom
        nom = df_filtre_client["nom_client"].iloc[0]
        show_metric_if_exists(i1, nom, "Nom du client")

        # LE type de client
        type = df_filtre_client["type_client"].iloc[0]
        show_metric_if_exists(i2, type, "Type du client")

        st.markdown("---")
        st.markdown("#### Informations Géographique")
        i_1, i_2, i_3, i_4 = st.columns(4)

        # Pays
        pays = df_filtre_client["pays"].iloc[0]
        show_metric_if_exists(i_1, pays, "Pays")

        # VIlle
        ville = df_filtre_client["ville"].iloc[0]
        show_metric_if_exists(i_2, ville, "Ville")

        # Departement
        dep = df_filtre_client["departement"].iloc[0]
        show_metric_if_exists(i_3, dep, "Département")

        # Code_postal
        code_post = df_filtre_client["code_postal"].iloc[0]
        show_metric_if_exists(i_4, code_post, "Code Postal")

        st.markdown("---")
        st.markdown("#### Contact")
        con1, con2, con3 = st.columns(3)

        # Code_postal
        tel = df_filtre_client["portable"].iloc[0]
        show_metric_if_exists(con1, tel, "Portable")

        # Code_postal
        fixe = df_filtre_client["fixe"].iloc[0]
        show_metric_if_exists(con2, fixe, "Fixe")

        # Email
        mail = df_filtre_client["email"].iloc[0]
        with con3:
            if pd.isna(mail):
                st.metric("e-Mail", "")
                st.info("Cette valeur n'est pas connue")
            else:
                st.metric("e-Mail", "")
                st.write(mail)

        site = df_filtre_client["siteweb"].iloc[0]
        if not pd.isna(site):
            st.markdown("#### Site Professionel")
            s1 = st.columns(1)
            show_metric_if_exists(s1, site, "Site web")

        # df_info_cli = df_info_cli[df_info_cli["nom_client"] == client]
        with st.expander("Afficher le dataframe des informations", expanded=False):
            st.dataframe(df_info_cli[df_info_cli["nom_client"] == client])
