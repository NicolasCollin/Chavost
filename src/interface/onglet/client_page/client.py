import streamlit as st

from src.utils.engineering import (
    df_clients,
    df_commande,
    df_stock,
    df_article,
    df_info_client,
)

from src.interface.onglet.client_page.features.db import make_con, register_tables
from src.interface.onglet.client_page.features.prepare import (
    prepare_client_filters,
)
from src.interface.onglet.client_page.features.queries import (
    query_nb_commande,
    query_tot_paye,
    query_produit_distincs,
    query_nb_tot_prod,
    query_suivi_temp,
    query_top_achat,
    query_suivi_temp_year,
)
from src.interface.onglet.client_page.features.viz import (
    build_fig_suivi,
    build_fig_top_achat,
    build_fig_suivi_year,
)
from src.interface.onglet.client_page.features.render import (
    render_kpis,
    metric_table_date,
    render_affichage_commande,
    render_info_client,
)


def client_tool():
    con = make_con()

    df = df_clients()
    df_sto = df_stock()
    df_com = df_commande()
    df_art = df_article()
    df_info = df_info_client()

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
        ##On affixche premièremen les informations importantes

        st.markdown("**Informations du client**")
        with st.expander("Afficher les informations", expanded=False):
            df_info_cli = df_info[
                [col for col in df_info.columns if not col.startswith("unname")]
            ]
            st.markdown("#### Informations personelles clients")
            render_info_client(df_info_cli, sel_clients)

        # On enregistre les bases de données en sql et on applique le filtre
        df_filtre, df_com_filtre, df_stock_filtred = prepare_client_filters(
            df, df_sto, df_com, sel_clients, df_art
        )

        st.markdown("## Résumé chiffré des commandes")
        con = register_tables(con, df_com_filtre, df_filtre, df_stock_filtred)

        with st.container(border=True):
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

        # st.markdown("## Suivi temporel des ventes par clients")

        sql_suivi_temp_df = query_suivi_temp(con)
        df_full = sql_suivi_temp_df

        st.markdown("## Suivi temporel des ventes")
        with st.container(border=True):
            fig_suivi = build_fig_suivi(df_full)
            st.plotly_chart(fig_suivi, use_container_width=True)
            with st.expander("Visualisation annuelle"):
                fig_suivi_year = build_fig_suivi_year(query_suivi_temp_year(con))
                st.plotly_chart(fig_suivi_year, use_container_width=True)
        st.markdown("## Visualisation des top ventes")

        with st.container(border=True):
            sql_top_achat_df = query_top_achat(con)

            fig_top_achat = build_fig_top_achat(sql_top_achat_df)
            st.plotly_chart(fig_top_achat)

        # création de la fonction qui regarde chaque commande
        st.markdown("---")
        if len(sel_clients) == 1:
            st.markdown("## Reherche des commandes par dates")
            dates_all = (
                df_stock_filtred["date_y"]
                .sort_values(ascending=False)
                .unique()
                .tolist()
            )
            sel_date = st.multiselect(
                "Rechercher une date de commande",
                options=dates_all,
                default=[],
                help="Tapez quelques lettres : des suggestions apparaissent automatiquement. Laissez vide pour tous les clients.",
            )
            # créationn des bases de donnéés contenant les filtres choisis
            df_com_filtre = df_com_filtre[df_com_filtre["date"].isin(sel_date)]
            df_order_client_by_dates = df_stock_filtred[
                df_stock_filtred["date_y"].isin(sel_date)
            ]

            # LEs infos principale de la commande
            if sel_date:
                with st.container(border=False):
                    metric_table_date(df_com_filtre, sel_date, df_order_client_by_dates)
                    with st.expander(
                        "📦 Affiché les détails des produits achetés", expanded=False
                    ):
                        render_affichage_commande(df_order_client_by_dates)
        st.markdown("---")
        st.write("La partie du tableau concernant le ou les clients choisis")
        st.dataframe(df_stock_filtred, use_container_width=True)

    else:
        st.info(
            "Veuillez entrez un ou plusieurs noms dans la bare de recherche (4 maximum pour des soucis de lisibilité)"
        )


if __name__ == "__main__":
    client_tool()  # Run the Streamlit client explorer entrypoint
