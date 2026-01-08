import pandas as pd
import plotly.express as px


def build_fig_top_cuvees(df: pd.DataFrame, value_col: str, title: str):
    """Barres horizontales : top cuvées."""
    if df.empty:
        return px.bar(title=title)

    d = df.sort_values(value_col, ascending=True)
    return px.bar(
        d,
        x=value_col,
        y="article",
        orientation="h",
        title=title,
        labels={"article": "Cuvée", value_col: value_col},
    )


def build_fig_evolution_quantite(df: pd.DataFrame):
    """Courbe mensuelle des quantités vendues."""
    if df.empty:
        return px.line(title="Quantités vendues par mois")

    return px.line(
        df,
        x="mois",
        y="quantite_vendue",
        markers=True,
        title="Quantités vendues par mois",
        labels={"mois": "Mois", "quantite_vendue": "Quantité vendue"},
    )


def build_fig_evolution_valeur(df: pd.DataFrame):
    """Courbe mensuelle de la valeur vendue."""
    if df.empty:
        return px.line(title="Valeur vendue par mois")

    return px.line(
        df,
        x="mois",
        y="valeur_ventes",
        markers=True,
        title="Valeur vendue par mois",
        labels={"mois": "Mois", "valeur_ventes": "Valeur vendue"},
    )


def build_fig_pareto_abc(df: pd.DataFrame):
    """Pareto (cumul) + seuils 80% et 95%."""
    if df.empty:
        return px.line(title="Pareto (cumul de la valeur)")

    fig = px.line(
        df,
        x="rang",
        y="cumul_part",
        markers=True,
        title="Pareto (cumul de la valeur vendue)",
        labels={"rang": "Rang", "cumul_part": "Part cumulée"},
    )
    fig.update_yaxes(tickformat=".0%")
    fig.add_hline(y=0.80, line_dash="dot")
    fig.add_hline(y=0.95, line_dash="dot")
    return fig


def build_fig_abc_repartition(df: pd.DataFrame):
    """Barres : nombre de cuvées par classe ABC."""
    if df.empty:
        return px.bar(title="Répartition ABC")

    rep = (
        df["classe_abc"]
        .value_counts()
        .rename_axis("classe_abc")
        .reset_index(name="nb_cuvees")
        .sort_values("classe_abc")
    )
    return px.bar(
        rep,
        x="classe_abc",
        y="nb_cuvees",
        title="Répartition ABC (nombre de cuvées)",
        labels={"classe_abc": "Classe", "nb_cuvees": "Nombre de cuvées"},
    )
