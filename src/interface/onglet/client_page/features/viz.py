import plotly.express as px
import plotly.graph_objects as go
import textwrap


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


def wrap_label(s, width=14):
    # wrap par largeur de caractères (simple et efficace)
    return "<br>".join(textwrap.wrap(str(s), width=width))


def build_fig_commande(df_use):
    ticktext_wrapped = [wrap_label(a, width=14) for a in df_use["article"]]

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
            tickvals=df_use["article"],
            ticktext=ticktext_wrapped,  # <-- wrap
            tickangle=0,  # <-- droit
            tickfont=dict(size=11),
            automargin=True,  # <-- laisse Plotly gérer la marge
        ),
        yaxis=dict(title="Quantité"),
        yaxis2=dict(title="Prix unitaire (€)", overlaying="y", side="right"),
        legend=dict(
            x=0.98,
            y=1.12,
            xanchor="right",
            yanchor="top",
            bgcolor="rgba(255,255,255,0.7)",
            bordercolor="rgba(0,0,0,0.2)",
            borderwidth=1,
        ),
        margin=dict(b=110),  # <-- plus de place en bas pour les labels
        height=520,  # <-- augmente si besoin
    )

    return fig_commande
