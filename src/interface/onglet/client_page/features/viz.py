import plotly.express as px
import plotly.graph_objects as go


def build_fig_suivi(df_full):
    fig_suivi = px.line(
        df_full,
        x="date",
        y="quantite",
        color="nom",
        markers=True,
        title="Suivi temporel du nombre de bouteilles vendues par client",
    )
    return fig_suivi


def build_fig_suivi_year(df_full):
    fig_suivi = px.line(
        df_full,
        x="annee",
        y="quantite",
        color="nom",
        markers=True,
        title="Suivi annuel du nombre de bouteilles vendues par client",
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


def build_fig_commande(df_use):
    fig_commande = go.Figure()
    fig_commande.add_bar(
        x=df_use["article"],
        y=df_use["quantite_reel"],
        name="Quantité",
        marker_color="steelblue",
    )
    fig_commande.add_scatter(
        x=df_use["article"],
        y=df_use["prix_unitaire"],
        name="Prix unitaire",
        mode="lines+markers",
        line=dict(color="red", width=3),
        yaxis="y2",
    )
    fig_commande.update_layout(
        title="Résumé graphique par commandes",
        xaxis=dict(
            tickmode="array",
            tickvals=df_use["article"],  # valeurs réelles
            ticktext=df_use["article_short"],
            tickangle=-25,
        ),
        yaxis=dict(
            title="Quantité",
        ),
        yaxis2=dict(
            title="Prix unitaire (€)",
            overlaying="y",
            side="right",
        ),
        legend=dict(
            x=0.98,
            y=1.18,
            xanchor="right",
            yanchor="top",
            bgcolor="rgba(255,255,255,0.7)",  # optionnel
            bordercolor="rgba(0,0,0,0.2)",  # optionnel
            borderwidth=1,
        ),
    )
    return fig_commande
