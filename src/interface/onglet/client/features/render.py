import streamlit as st


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
            val = float(sql_tot_paye_df["tot_paye"].round(2).iloc[0])
            c2.metric("Total payé par le client (en €)", val)

        with c3:
            val = int(sql_produit_distincs_df["prod_diff"].iloc[0])
            c3.metric("Nombre de produits distincts achetés", val)

        with c4:
            val = float(sql_nb_tot_prod_df["nombre_produits"].iloc[0])
            c4.metric("Nombre total de produit achaté", val)
