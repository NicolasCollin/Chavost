def query_nb_commande(con):
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
    return sql_nb_commande_df


def query_tot_paye(con):
    sql_tot_paye = """
        select
            sum(net_payer) as tot_paye,
            nom_du_client as nom
        from
            commandes_select
        group by nom_du_client
    """
    sql_tot_paye_df = con.execute(sql_tot_paye).df()
    return sql_tot_paye_df


def query_produit_distincs(con):
    sql_produit_distincs = """
    select
        count(distinct article) as prod_diff,
        nom_du_client as nom
    from
        stock_select
    group by nom_du_client
    """
    sql_produit_distincs_df = con.execute(sql_produit_distincs).df()
    return sql_produit_distincs_df


def query_nb_tot_prod(con):
    sql_nb_tot_prod = """
    select
        sum(-quantit_) as nombre_produits,
        nom_du_client as nom
    from
        stock_select
    group by nom_du_client
    """
    sql_nb_tot_prod_df = con.execute(sql_nb_tot_prod).df()
    return sql_nb_tot_prod_df


def query_suivi_temp(con):
    sql_suivi_temp = """
    select
        nom_du_client as nom,
        sum(-quantit_) as quantite,
        mois_annee
    from stock_select
    group by mois_annee, nom_du_client
    order by mois_annee
    """
    sql_suivi_temp_df = con.execute(sql_suivi_temp).df()
    return sql_suivi_temp_df


def query_top_achat(con):
    sql_top_achat = """
    select
        article,
        sum(-quantit_) as quantite_tot,
        nom_du_client as nom
    from stock_select
    group by article, nom
    order by nom
    """
    sql_top_achat_df = con.execute(sql_top_achat).df()
    return sql_top_achat_df
