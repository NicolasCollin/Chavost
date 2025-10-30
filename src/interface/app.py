# ====================== Chavost Dashboard (polished) ======================
from pathlib import Path  # path ops
from typing import Any  # NEW
import io  # csv export buffer
import numpy as np  # numeric ops
import pandas as pd  # data wrangling
import plotly.express as px  # charts
import streamlit as st  # UI

# ---------- Page config & style ----------
st.set_page_config(page_title="Chavost — Tableau de bord", layout="wide")  # wide layout

# Plotly look & feel (simple brand)                                            # theme
px.defaults.template = (
    "plotly_white"  # clean background                     # default template
)
BRAND_COLORS = (
    px.colors.qualitative.Set2
)  # friendly qualitative palette     # color palette


# ---------- Helpers ----------
def fmt_int(x: float | int) -> str:  # pretty integers
    """Format integer with space as thousands separator; return em dash on error."""
    try:
        return f"{int(x):,}".replace(",", " ")  # e.g., 12 345
    except Exception:
        return "—"


def load_csv_safely(
    path_or_buf: Any,
) -> pd.DataFrame:  # accept file path or UploadedFile
    """Load CSV with multiple parsing attempts to handle different formats."""
    for kwargs in (
        dict(sep=",", thousands=",", decimal="."),
        dict(sep=",", thousands=" ", decimal=","),
        dict(sep=","),
        dict(sep=";"),
    ):
        try:
            df = pd.read_csv(path_or_buf, **kwargs)
            if df.shape[1] >= 2:
                return df
        except Exception:
            continue
    return pd.read_csv(path_or_buf)  # last resort


# ---------- Data loading ----------
DATA_PATH = (
    Path(__file__).parents[2] / "data" / "base_cryptee.csv"
)  # ../../data/base_cryptee.csv


@st.cache_data(show_spinner=False)
def get_data(
    uploaded: Any,
) -> pd.DataFrame:  # uploaded can be Streamlit UploadedFile or None
    """Load and clean data from CSV file (uploaded or default)."""
    if uploaded is not None:
        df = load_csv_safely(uploaded)  # user file
    else:
        if not DATA_PATH.exists():
            raise FileNotFoundError(f"CSV introuvable : {DATA_PATH}")
        df = load_csv_safely(DATA_PATH)  # project file

    # Normalize and type                                                          # clean schema
    df.columns = [c.strip().lower() for c in df.columns]  # lower snake-ish
    expected = [
        "annee",
        "type_produit",
        "nom_produit",
        "quantite",
        "prix",
        "vecteur_id",
    ]  # required cols
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes dans le CSV : {missing}")

    df["annee"] = pd.to_numeric(df["annee"], errors="coerce").astype(
        "Int64"
    )  # year as nullable int
    df["quantite"] = pd.to_numeric(df["quantite"], errors="coerce")  # qty numeric
    df["prix"] = pd.to_numeric(df["prix"], errors="coerce")  # price/amount numeric
    df["type_produit"] = df["type_produit"].astype(str)  # category
    df["nom_produit"] = df["nom_produit"].astype(str)  # product name
    df["vecteur_id"] = df["vecteur_id"].astype(str)  # channel id (string)
    df = df.dropna(subset=["annee", "quantite", "prix"]).copy()  # keep valid rows

    # Create categorical year string to avoid 2023.5 ticks                        # <-- fix weird year ticks
    df["annee_str"] = df["annee"].astype("Int64").astype(str)  # categorical year labels
    return df


# ---------- Sidebar: data source ----------
with st.sidebar:
    st.header("Données")  # data section
    up = st.file_uploader(
        "Importer un CSV (optionnel)",
        type=["csv"],
        help="Laisse vide pour utiliser data/base_cryptee.csv",
    )
    price_is_unit = st.toggle(
        "‘prix’ est un prix unitaire",
        value=False,
        help="Active si ‘prix’ correspond à un PU. Le CA sera alors quantité × prix. Sinon, ‘prix’ est déjà un montant total.",
    )
    st.caption("Conseil : garde la même structure de colonnes.")

# ---------- Load & derive ----------
try:
    df = get_data(up)  # read data
except Exception as e:
    st.error(f"Erreur de chargement : {e}")
    st.stop()

df["canal"] = df["vecteur_id"]  # clearer display name for channel
df["ca"] = (
    df["quantite"] * df["prix"] if price_is_unit else df["prix"]
)  # revenue definition

# ---------- Hero / Onboarding ----------
st.title("Chavost — Tableau de bord ventes")  # title
with st.expander("🧭 Comment utiliser (guide rapide)", expanded=True):
    st.markdown(
        """
**Objectif.** Explorer rapidement les ventes par année, type de produit, canal et produit.

**Étapes :**
1. *(Facultatif)* Importez un CSV dans la barre latérale ; sinon, l’app lit `data/base_cryptee.csv`.
2. Choisissez si `prix` est un **prix unitaire** (alors CA = quantité × prix) ou un **montant total**.
3. Filtrez par **Années**, **Types de produit**, **Canaux** et recherchez un **produit**.
4. Parcourez les onglets : *Vue d’ensemble*, *Évolution*, *Types & canaux*, *Produits*, *Analyse des prix*, *Table / Export*.

**Glossaire**
- **Type de produit** : famille (ex. Champagne, Ratafia…)
- **Canal** : chemin de vente (identifiant anonymisé `vecteur_id`)
- **CA** : chiffre d’affaires
        """
    )

# ---------- Sidebar: filters ----------
with st.sidebar:
    st.header("Filtres")
    years_all = [
        y for y in df["annee"].dropna().astype(int).sort_values().unique().tolist()
    ]  # all years as int
    years_all_str = [str(y) for y in years_all]  # string labels
    sel_years = st.multiselect(
        "Années",
        years_all_str,
        default=years_all_str,
        help="Limite l’analyse à certaines années.",
    )
    types_all = sorted(df["type_produit"].dropna().unique().tolist())
    sel_types = st.multiselect(
        "Types de produit",
        types_all,
        default=types_all,
        help="Filtrer une ou plusieurs familles.",
    )
    canals_all = sorted(df["canal"].dropna().unique().tolist())
    sel_canals = st.multiselect(
        "Canaux (vente)",
        canals_all,
        default=canals_all,
        help="Chaque identifiant correspond à un canal.",
    )
    name_query = st.text_input(
        "Recherche produit (contient)",
        help="Filtre sur ‘nom_produit’ (sensible aux accents).",
    )
    st.markdown("---")
    top_n = st.slider(
        "Top N produits",
        3,
        30,
        10,
        step=1,
        help="Nombre de produits affichés dans le Top.",
    )

mask = (
    df["annee_str"].isin(sel_years)
    & df["type_produit"].isin(sel_types)
    & df["canal"].isin(sel_canals)
)  # filter base
if name_query.strip():
    mask &= df["nom_produit"].str.contains(
        name_query.strip(), case=False, na=False
    )  # name filter

fdf = df.loc[mask].copy()  # filtered df
if fdf.empty:
    st.warning(
        "Aucune ligne avec ces filtres. Ajustez les sélections dans la barre latérale."
    )
    st.stop()

# ---------- Data quality quick view ----------
with st.expander("🧪 Qualité des données (aperçu)"):
    dup_subset = [
        "annee",
        "type_produit",
        "nom_produit",
        "canal",
        "quantite",
        "prix",
    ]  # candidate key
    nb_dup = int(fdf.duplicated(subset=dup_subset, keep=False).sum())  # possible dups
    miss_pct = fdf.isna().mean().round(3) * 100  # missing %
    c1, c2, c3 = st.columns(3)
    c1.metric("Lignes filtrées", fmt_int(len(fdf)))
    c2.metric("Doublons potentiels", fmt_int(nb_dup))
    c3.metric(
        "Colonnes numériques", fmt_int(fdf.select_dtypes(include=[np.number]).shape[1])
    )
    st.caption(
        "Doublons calculés sur (année, type_produit, nom_produit, canal, quantite, prix)."
    )
    miss_top = miss_pct.sort_values(ascending=False).head(20)
    if not miss_top.empty:
        st.dataframe(miss_top.rename("missing_%"), use_container_width=True)

# ---------- KPIs ----------
k1, k2, k3, k4 = st.columns(4)
k1.metric("Lignes", fmt_int(len(fdf)))
k2.metric("Produits distincts", fmt_int(fdf["nom_produit"].nunique()))
k3.metric("Quantité totale", fmt_int(np.nansum(fdf["quantite"])))
k4.metric("Chiffre d’affaires", fmt_int(np.nansum(fdf["ca"])))
st.divider()

# ---------- Tabs ----------
tab_overview, tab_time, tab_types, tab_products, tab_prices, tab_table = st.tabs(
    [
        "Vue d’ensemble",
        "Évolution",
        "Types & canaux",
        "Produits",
        "Analyse des prix",
        "Table / Export",
    ]
)

# ===================== Tab: Overview =====================
with tab_overview:
    st.markdown("**Résumé visuel :** volumes et CA par année et par type.")
    c1, c2 = st.columns([2, 1])

    # CA by year (categorical x using year string)                                 # bar
    by_year = fdf.groupby(["annee", "annee_str"], as_index=False).agg(
        ca=("ca", "sum"), qte=("quantite", "sum")
    )
    if not by_year.empty:
        fig = px.bar(
            by_year.sort_values("annee"),
            x="annee_str",
            y="ca",
            title="Chiffre d’affaires par année",
            color_discrete_sequence=BRAND_COLORS,
        )
        fig.update_layout(xaxis_title="Année", yaxis_title="CA")
        c1.plotly_chart(fig, use_container_width=True)

    # Pie share by product type with % in legend                                    # pie with % in legend
    by_type = (
        fdf.groupby("type_produit", as_index=False)["ca"]
        .sum()
        .sort_values("ca", ascending=False)
    )
    if not by_type.empty:
        total = by_type["ca"].sum()
        by_type["label"] = by_type.apply(
            lambda r: f"{r['type_produit']} — {100*r['ca']/total:.1f}%", axis=1
        )
        pie = px.pie(
            by_type,
            names="label",
            values="ca",
            title="Répartition du CA par type",
            color_discrete_sequence=BRAND_COLORS,
        )
        pie.update_traces(
            textinfo="percent",
            hovertemplate="%{label}<br>CA=%{value:,.0f}<extra></extra>",
        )
        c2.plotly_chart(pie, use_container_width=True)

# ===================== Tab: Time =====================
with tab_time:
    st.markdown("**Tendances annuelles** — sélectionnez la métrique à tracer.")
    metric_choice = st.selectbox(
        "Métrique", ["ca", "quantite"], index=0, help="CA ou Quantité."
    )

    by_year = fdf.groupby(["annee", "annee_str"], as_index=False).agg(
        ca=("ca", "sum"), qte=("quantite", "sum")
    )
    if not by_year.empty:
        line = px.line(
            by_year.sort_values("annee"),
            x="annee_str",
            y="ca" if metric_choice == "ca" else "qte",
            markers=True,
            title=f"Évolution de {metric_choice.upper()}",
            color_discrete_sequence=BRAND_COLORS,
        )
        line.update_layout(xaxis_title="Année", yaxis_title=metric_choice.upper())
        st.plotly_chart(line, use_container_width=True)

    bt = fdf.groupby(["annee", "annee_str", "type_produit"], as_index=False)["ca"].sum()
    if not bt.empty:
        fig = px.bar(
            bt.sort_values("annee"),
            x="annee_str",
            y="ca",
            color="type_produit",
            barmode="group",
            title="CA par année et type",
            color_discrete_sequence=BRAND_COLORS,
        )
        fig.update_layout(xaxis_title="Année", yaxis_title="CA")
        st.plotly_chart(fig, use_container_width=True)

# ===================== Tab: Types & channels =====================
with tab_types:
    st.markdown("**Comparatif par familles et par canaux de vente.**")
    c1, c2 = st.columns(2)

    by_type = (
        fdf.groupby("type_produit", as_index=False)["ca"]
        .sum()
        .sort_values("ca", ascending=False)
    )
    if not by_type.empty:
        bar_t = px.bar(
            by_type,
            x="type_produit",
            y="ca",
            title="CA par type de produit",
            color_discrete_sequence=BRAND_COLORS,
        )
        bar_t.update_layout(xaxis_title="Type", yaxis_title="CA")
        c1.plotly_chart(bar_t, use_container_width=True)

    by_canal = (
        fdf.groupby("canal", as_index=False)["ca"]
        .sum()
        .sort_values("ca", ascending=False)
    )
    if not by_canal.empty:
        bar_c = px.bar(
            by_canal,
            x="canal",
            y="ca",
            title="CA par canal (vente)",
            color_discrete_sequence=BRAND_COLORS,
        )
        bar_c.update_layout(xaxis_title="Canal", yaxis_title="CA")
        c2.plotly_chart(bar_c, use_container_width=True)

# ===================== Tab: Products =====================
with tab_products:
    st.markdown("**Top produits et analyse détaillée par produit.**")

    top_ca = (
        fdf.groupby("nom_produit", as_index=False)
        .agg(ca=("ca", "sum"), quantite=("quantite", "sum"))
        .sort_values("ca", ascending=False)
        .head(top_n)
    )
    c1, c2 = st.columns(2)
    if not top_ca.empty:
        bar_top = px.bar(
            top_ca,
            x="nom_produit",
            y="ca",
            title=f"Top {top_n} produits — CA",
            color_discrete_sequence=BRAND_COLORS,
        )
        bar_top.update_layout(xaxis_title="Produit", yaxis_title="CA")
        c1.plotly_chart(bar_top, use_container_width=True)

        bar_q = px.bar(
            top_ca,
            x="nom_produit",
            y="quantite",
            title=f"Top {top_n} produits — Quantités",
            color_discrete_sequence=BRAND_COLORS,
        )
        bar_q.update_layout(xaxis_title="Produit", yaxis_title="Quantité")
        c2.plotly_chart(bar_q, use_container_width=True)

    prods = top_ca["nom_produit"].tolist() or sorted(
        fdf["nom_produit"].unique().tolist()
    )
    sel_prod = st.selectbox(
        "Produit (détail)",
        prods,
        help="Choisissez un produit pour voir son historique.",
    )
    if sel_prod:
        p = (
            fdf.loc[fdf["nom_produit"] == sel_prod]
            .groupby(["annee", "annee_str"], as_index=False)
            .agg(ca=("ca", "sum"), quantite=("quantite", "sum"))
            .sort_values("annee")
        )
        if not p.empty:
            fig1 = px.bar(
                p,
                x="annee_str",
                y="ca",
                title=f"CA par année — {sel_prod}",
                color_discrete_sequence=BRAND_COLORS,
            )
            fig2 = px.line(
                p,
                x="annee_str",
                y="quantite",
                markers=True,
                title=f"Quantités par année — {sel_prod}",
                color_discrete_sequence=BRAND_COLORS,
            )
            st.plotly_chart(fig1, use_container_width=True)
            st.plotly_chart(fig2, use_container_width=True)

# ===================== Tab: Prices =====================
with tab_prices:
    st.markdown(
        "**Structure des prix** — distribution, écarts entre types et relation prix-quantité."
    )
    c1, c2 = st.columns(2)

    if fdf["prix"].notna().sum() > 0:
        hist = px.histogram(
            fdf,
            x="prix",
            nbins=40,
            title="Distribution du champ ‘prix’",
            color_discrete_sequence=BRAND_COLORS,
        )
        c1.plotly_chart(hist, use_container_width=True)

    if fdf["type_produit"].nunique() > 0:
        box = px.box(
            fdf,
            x="type_produit",
            y="prix",
            points="outliers",
            title="Prix par type de produit",
            color_discrete_sequence=BRAND_COLORS,
        )
        c2.plotly_chart(box, use_container_width=True)

    if fdf["quantite"].notna().sum() > 0:
        sc = px.scatter(
            fdf,
            x="quantite",
            y="prix",
            color="type_produit",
            title="Prix vs Quantité",
            hover_data=["nom_produit", "annee_str", "canal"],
            color_discrete_sequence=BRAND_COLORS,
        )
        st.plotly_chart(sc, use_container_width=True)

# ===================== Tab: Table / Export =====================
with tab_table:
    st.markdown("**Table filtrée** — téléchargez le sous-ensemble courant en CSV.")
    st.dataframe(fdf, use_container_width=True, height=480)
    buf = io.StringIO()
    fdf.to_csv(buf, index=False)
    st.download_button(
        "Télécharger (CSV)",
        buf.getvalue(),
        file_name="export_filtre.csv",
        mime="text/csv",
    )

# ---------- Footer ----------
st.caption(
    "Astuce : utilisez les outils Plotly (📷, 🔎) au-dessus des graphiques pour exporter/zoomer. Les paramètres se trouvent dans la barre latérale."
)
