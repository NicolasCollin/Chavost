import streamlit as st
from src.utils.engineering import df_clients, df_commande, df_stock
import duckdb

con = duckdb.connect(database=":memory:")
con.register("commandes", df_commande())
con.register("clients", df_clients())
con.register("stock", df_stock())


def client_tool():
    st.markdown("---")
    st.title("👥 Explorateur de client")
    st.markdown(
        """
Bienvenue sur **L'explorateur de clients** de Chavost.
**Dans cette partie** vous allez pouvoir extraire **toutes** les informations possible relatives aux clients qui ont acheté.
"""
    )
    df = df_clients()
    df_sto = df_stock()
    df_com = df_commande()

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
        df_filtre = df[df["nom_du_client"].astype(str).isin(sel_clients)].copy()
        df_com_filtre = df_com[df_com["nom_du_client"].isin(sel_clients)]
        df_stock_filtred = df_com_filtre.merge(df_sto, on="n_document", how="left")
        con.register("commandes_select", df_com_filtre)
        con.register("clients_select", df_filtre)
        con.register("stock_select", df_stock_filtred)

        c1, c2, c3, c4 = st.columns(4)
        # pour travailler
        # st.dataframe(df_com[df_com["nom_du_client"].isin(sel_clients)])

        # total de commandes
        sql_nb_commande = """
            select
                count(*) as nb_comm,
                nom_du_client as nom
            from
                commandes_select
            where n_document like 'CM%'
            OR n_document LIKE 'FA%'
            group by nom_du_client
        """
        sql_nb_commande_df = con.execute(sql_nb_commande).df()

        # total payé
        sql_tot_paye = """
            select
                sum(net_payer) as tot_paye,
                nom_du_client as nom
            from
                commandes_select
            group by nom_du_client
        """
        sql_tot_paye_df = con.execute(sql_tot_paye).df()

        # Nombre de produit différents achetés
        sql_produit_distincs = """
        select
            count(distinct article) as prod_diff,
            nom_du_client as nom
        from
            stock_select
        group by nom_du_client
        """
        sql_produit_distincs_df = con.execute(sql_produit_distincs).df()

        # Nombre de produit total
        sql_nb_tot_prod = """
        select
            sum(-quantit_) as nombre_produits,
            nom_du_client as nom
        from
            stock_select
        group by nom_du_client
        """
        sql_nb_tot_prod_df = con.execute(sql_nb_tot_prod).df()

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
                val = sql_nb_commande_df["nb_comm"]
                c1.metric("Nombre de commandes passées par le client", val)
            with c2:
                val = sql_tot_paye_df["tot_paye"]
                c2.metric("Total payé par le client (en €)", val)
            with c3:
                val = sql_produit_distincs_df["prod_diff"]
                c3.metric("Nombre de produits distincts achetés", val)
            with c4:
                val = sql_nb_tot_prod_df["nombre_produits"]
                c4.metric("Nombre total de produit achaté", val)

        # Pour bosser n affiche ca
        # st.dataframe(df_stock_filtred,hide_index=True)

        st.markdown("---")
        st.write("La partie du tableau concernant le ou les clients choisis")
        st.dataframe(df_filtre, use_container_width=True)
    else:
        st.info(
            "Vuillez entrez un ou plusieurs noms dans la bare de recherche (4 maximum pour des soucis de lisibilité)"
        )


if __name__ == "__main__":
    client_tool()
