import streamlit as st
from src.utils.engineering import df_clients, df_commande, df_stock

from src.interface.onglet.client.features.db import make_con, register_tables
from src.interface.onglet.client.features.prepare import (
    prepare_client_filters,
    build_df_full,
)
from src.interface.onglet.client.features.queries import (
    query_nb_commande,
    query_tot_paye,
    query_produit_distincs,
    query_nb_tot_prod,
    query_suivi_temp,
    query_top_achat,
)
from src.interface.onglet.client.features.viz import (
    build_fig_suivi,
    build_fig_top_achat,
)
from src.interface.onglet.client.features.render import render_kpis


def client_tool(df, df_sto, df_com):
    con = make_con()

    st.markdown("---")
    st.title("👥 Explorateur de client")
    st.markdown(
        """
Bienvenue sur **L'explorateur de clients** de Chavost.
**Dans cette partie** vous allez pouvoir extraire **toutes** les informations possible relatives aux clients qui ont acheté.
"""
    )

    # ✅ Barre de recherche "intelligente" (autocomplete)
    clients_all = (
        df["nom_du_client"].dropna().astype(str).sort_values().unique().tolist()
    )

    sel_clients = st.multiselect(
        "Rechercher un client",
        options=clients_all,
        default=[],
        help="Tapez quelques lettres : des suggestions apparaissent automatiquement. Laissez vide pour tous les clients.",
    )

    if sel_clients:
        # On enregistre les bases de données en sql et on applique le filtre
        df_filtre, df_com_filtre, df_stock_filtred = prepare_client_filters(
            df, df_sto, df_com, sel_clients
        )

        con = register_tables(con, df_com_filtre, df_filtre, df_stock_filtred)

        c1, c2, c3, c4 = st.columns(4)

        # total de commandes
        sql_nb_commande_df = query_nb_commande(con)

        # total payé
        sql_tot_paye_df = query_tot_paye(con)

        # Nombre de produit différents achetés
        sql_produit_distincs_df = query_produit_distincs(con)

        # Nombre de produit total
        sql_nb_tot_prod_df = query_nb_tot_prod(con)

        render_kpis(
            sel_clients,
            c1,
            c2,
            c3,
            c4,
            sql_nb_commande_df,
            sql_tot_paye_df,
            sql_produit_distincs_df,
            sql_nb_tot_prod_df,
        )

        st.markdown("## Suivi temporel des ventes par clients")

        sql_suivi_temp_df = query_suivi_temp(con)
        df_full = build_df_full(sql_suivi_temp_df)

        fig_suivi = build_fig_suivi(df_full)
        st.plotly_chart(fig_suivi, use_container_width=True)

        st.markdown("## Visualisation des top ventes parclients")

        sql_top_achat_df = query_top_achat(con)

        fig_top_achat = build_fig_top_achat(sql_top_achat_df)
        st.plotly_chart(fig_top_achat)

        st.markdown("---")
        st.write("La partie du tableau concernant le ou les clients choisis")
        st.dataframe(df_filtre, use_container_width=True)

    else:
        st.info(
            "Veuillez entrez un ou plusieurs noms dans la bare de recherche (4 maximum pour des soucis de lisibilité)"
        )


if __name__ == "__main__":
    client_tool(df_clients(), df_stock(), df_commande())
