import plotly.express as px


def build_fig_suivi(df_full):
    fig_suivi = px.line(
        df_full,
        x="mois_annee",
        y="quantite",
        color="nom",
        markers=True,
        title="Suivi temporel du nombre de bouteilles vendues par client",
    )
    return fig_suivi


def build_fig_top_achat(sql_top_achat_df):
    fig_top_achat = px.bar(
        sql_top_achat_df,
        x="nom",
        y="quantite_tot",
        color="article",
        title="Ensemble des achats effectués par client",
        barmode="group",
    )
    return fig_top_achat
