"""Visualisations Plotly pour la page *client*.

Objectif
--------
Ce module regroupe les fonctions de création de figures Plotly utilisées
sur la page *client*.

Conventions
-----------
- Le suivi temporel mensuel utilise `mois_annee` en abscisse.
- Le suivi annuel utilise `annee` en abscisse.
- Les fonctions retournent toujours un `plotly.graph_objects.Figure`.
"""

import textwrap

import plotly.express as px
import plotly.graph_objects as go


def build_fig_suivi(df_full):
    """Construit la figure de suivi mensuel.

    Paramètres
    ----------
    df_full : pd.DataFrame
        Doit contenir au minimum :
        - `nom` (client)
        - `mois_annee` (YYYY-MM)
        - `quantite`

    Retour
    ------
    plotly.graph_objects.Figure
        Courbe Plotly du suivi mensuel.
    """

    fig_suivi = px.line(
        df_full,
        x="mois_annee",
        y="quantite",
        color="nom",
        markers=True,
        title="Suivi temporel du nombre de bouteilles vendues par client",
    )
    return fig_suivi


def build_fig_suivi_year(df_full):
    """Construit la figure de suivi annuel.

    Paramètres
    ----------
    df_full : pd.DataFrame
        Doit contenir au minimum :
        - `nom` (client)
        - `annee`
        - `quantite`

    Retour
    ------
    plotly.graph_objects.Figure
        Courbe Plotly du suivi annuel.
    """

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
    """Construit la figure des achats par client (barres groupées).

    Paramètres
    ----------
    sql_top_achat_df : pd.DataFrame
        Doit contenir au minimum :
        - `nom`
        - `article`
        - `quantite_tot`

    Retour
    ------
    plotly.graph_objects.Figure
        Bar chart des achats.
    """

    fig_top_achat = px.bar(
        sql_top_achat_df,
        x="nom",
        y="quantite_tot",
        color="article",
        title="Ensemble des achats effectués par client",
        barmode="group",
    )
    return fig_top_achat


def wrap_label(label, width=14):
    """Découpe une étiquette en plusieurs lignes (HTML <br>)."""

    return "<br>".join(textwrap.wrap(str(label), width=width))


def build_fig_commande(df_use):
    """Construit un graphique double axe (quantité + prix unitaire) pour une commande."""

    ticktext_wrapped = [wrap_label(a, width=14) for a in df_use["article"]]

    df_use = df_use.sort_values(by="prix_unitaire", ascending=False)

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
            ticktext=ticktext_wrapped,
            tickangle=0,
            tickfont=dict(size=11),
            automargin=True,
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
        margin=dict(b=110),
        height=520,
    )

    return fig_commande
