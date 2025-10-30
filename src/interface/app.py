import io  # in-memory buffers
from pathlib import Path  # file paths
import numpy as np  # numeric ops
import pandas as pd  # data handling
import plotly.express as px  # charts
import streamlit as st  # UI

# ---------------- Page config ---------------- #
st.set_page_config(page_title="Chavost - Tableau de bord", layout="wide")

# ---------------- Chargement des données ---------------- #
DATA_PATH = (
    Path(__file__).parents[2] / "data" / "base_cryptee.csv"
)  # ../.. /data/base_cryptee.csv


@st.cache_data(show_spinner=False)
def load_data(path: Path) -> pd.DataFrame:
    # On essaie d'être robuste aux formats (milliers/decimal)
    for kwargs in (
        dict(sep=",", thousands=",", decimal="."),  # 12,345.6
        dict(sep=",", thousands=" ", decimal=","),  # 12 345,6
        dict(sep=","),
    ):
        try:
            df = pd.read_csv(path, **kwargs)
            break
        except Exception:
            df = None
    if df is None:
        raise RuntimeError(
            "Impossible de lire le CSV. Vérifie le séparateur et les formats numériques."
        )
    # Normalisation noms colonnes
    df.columns = [c.strip().lower() for c in df.columns]
    # Cast colonnes attendues
    expected = [
        "annee",
        "type_produit",
        "nom_produit",
        "quantite",
        "prix",
        "vecteur_id",
    ]
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(f"Colonnes manquantes: {missing}")
    # Types
    df["annee"] = pd.to_numeric(df["annee"], errors="coerce").astype("Int64")
    df["quantite"] = pd.to_numeric(df["quantite"], errors="coerce")
    df["prix"] = pd.to_numeric(df["prix"], errors="coerce")
    df["type_produit"] = df["type_produit"].astype(str)
    df["nom_produit"] = df["nom_produit"].astype(str)
    df["vecteur_id"] = df["vecteur_id"].astype(str)
    # Lignes valides
    return df.dropna(subset=["annee", "quantite", "prix"]).copy()


# Source de données : fichier local avec possibilité d’upload
with st.sidebar:
    st.header("Données")
    uploaded = st.file_uploader("Uploader un CSV (optionnel)", type=["csv"])
    prix_is_unit = st.toggle(
        "Le champ 'prix' est un prix unitaire",
        value=False,
        help="Si activé: chiffre d'affaires = quantite × prix. Sinon: CA = prix.",
    )
    st.markdown("---")
    st.caption("Si aucun fichier n'est chargé, l'appli lit `data/base_cryptee.csv`.")

df = None
if uploaded is not None:
    df = load_data(uploaded)
else:
    df = load_data(DATA_PATH)

# Variable de chiffre d'affaires
if prix_is_unit:
    df["ca"] = df["quantite"] * df["prix"]
else:
    df["ca"] = df["prix"]

# ---------------- Filtres ---------------- #
with st.sidebar:
    st.header("Filtres")
    years = sorted([int(x) for x in df["annee"].dropna().unique()])
    sel_years = st.multiselect("Années", years, default=years)
    types = sorted(df["type_produit"].dropna().unique().tolist())
    sel_types = st.multiselect("Types de produit", types, default=types)
    vects = sorted(df["vecteur_id"].dropna().unique().tolist())
    sel_vects = st.multiselect("Vecteurs (canaux)", vects, default=vects)
    q_name = st.text_input("Recherche produit (contient)")
    st.markdown("---")
    top_n = st.slider("Top N produits", 3, 30, 10, step=1)

mask = (
    df["annee"].isin(sel_years)
    & df["type_produit"].isin(sel_types)
    & df["vecteur_id"].isin(sel_vects)
)
if q_name.strip():
    mask &= df["nom_produit"].str.contains(q_name.strip(), case=False, na=False)

fdf = df.loc[mask].copy()

# ---------------- KPIs ---------------- #
st.title("Tableau de bord ventes")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Lignes", f"{len(fdf):,}".replace(",", " "))
with c2:
    st.metric(
        "Produits distincts", f"{fdf['nom_produit'].nunique():,}".replace(",", " ")
    )
with c3:
    st.metric(
        "Quantité totale", f"{int(np.nansum(fdf['quantite'])):,}".replace(",", " ")
    )
with c4:
    st.metric("Chiffre d'affaires", f"{np.nansum(fdf['ca']):,.0f}".replace(",", " "))

st.markdown("---")

# ---------------- Onglets ---------------- #
tab_overview, tab_evol, tab_types, tab_products, tab_prices, tab_table = st.tabs(
    [
        "Vue d'ensemble",
        "Évolution",
        "Types & canaux",
        "Produits",
        "Analyse des prix",
        "Table",
    ]
)

# ---- Vue d'ensemble ---- #
with tab_overview:
    c1, c2 = st.columns([2, 1])
    # CA par année (barres)
    by_year = fdf.groupby("annee", dropna=True, as_index=False).agg(
        ca=("ca", "sum"), qte=("quantite", "sum")
    )
    if not by_year.empty:
        fig = px.bar(
            by_year.sort_values("annee"),
            x="annee",
            y="ca",
            title="Chiffre d'affaires par année",
        )
        fig.update_layout(xaxis_title="Année", yaxis_title="CA")
        c1.plotly_chart(fig, use_container_width=True)
    # Répartition par type (camembert)
    by_type = (
        fdf.groupby("type_produit", as_index=False)["ca"]
        .sum()
        .sort_values("ca", ascending=False)
    )
    if not by_type.empty:
        pie = px.pie(
            by_type, names="type_produit", values="ca", title="Répartition CA par type"
        )
        c2.plotly_chart(pie, use_container_width=True)

# ---- Évolution ---- #
with tab_evol:
    c1, c2 = st.columns(2)
    # Série temporelle CA
    if not by_year.empty:
        line = px.line(
            by_year.sort_values("annee"),
            x="annee",
            y="ca",
            markers=True,
            title="Évolution du CA",
        )
        c1.plotly_chart(line, use_container_width=True)
        # Tendance quantités
        line_q = px.line(
            by_year.sort_values("annee"),
            x="annee",
            y="qte",
            markers=True,
            title="Évolution des quantités",
        )
        c2.plotly_chart(line_q, use_container_width=True)
    # CA par année et type
    bt = fdf.groupby(["annee", "type_produit"], as_index=False)["ca"].sum()
    if not bt.empty:
        fig = px.bar(
            bt,
            x="annee",
            y="ca",
            color="type_produit",
            barmode="group",
            title="CA par année et type",
        )
        st.plotly_chart(fig, use_container_width=True)

# ---- Types & canaux ---- #
with tab_types:
    c1, c2 = st.columns(2)
    # CA par type
    if not by_type.empty:
        bar_t = px.bar(
            by_type, x="type_produit", y="ca", title="CA par type de produit"
        )
        bar_t.update_layout(xaxis_title="Type", yaxis_title="CA")
        c1.plotly_chart(bar_t, use_container_width=True)
    # CA par vecteur
    by_vec = (
        fdf.groupby("vecteur_id", as_index=False)["ca"]
        .sum()
        .sort_values("ca", ascending=False)
    )
    if not by_vec.empty:
        bar_v = px.bar(by_vec, x="vecteur_id", y="ca", title="CA par vecteur (canal)")
        bar_v.update_layout(xaxis_title="Vecteur", yaxis_title="CA")
        c2.plotly_chart(bar_v, use_container_width=True)

# ---- Produits ---- #
with tab_products:
    # Top produits par CA
    top_ca = (
        fdf.groupby("nom_produit", as_index=False)
        .agg(ca=("ca", "sum"), quantite=("quantite", "sum"))
        .sort_values("ca", ascending=False)
        .head(top_n)
    )
    c1, c2 = st.columns(2)
    if not top_ca.empty:
        bar_top = px.bar(
            top_ca, x="nom_produit", y="ca", title=f"Top {top_n} produits (CA)"
        )
        bar_top.update_layout(xaxis_title="Produit", yaxis_title="CA")
        c1.plotly_chart(bar_top, use_container_width=True)
        # Quantités correspondantes
        bar_q = px.bar(
            top_ca,
            x="nom_produit",
            y="quantite",
            title=f"Top {top_n} produits (quantités)",
        )
        bar_q.update_layout(xaxis_title="Produit", yaxis_title="Quantité")
        c2.plotly_chart(bar_q, use_container_width=True)

    # Détail produit: CA par année sur produit sélectionné
    prods = top_ca["nom_produit"].tolist() or sorted(
        fdf["nom_produit"].unique().tolist()
    )
    sel_prod = st.selectbox("Produit (détail)", prods)
    if sel_prod:
        p = (
            fdf.loc[fdf["nom_produit"] == sel_prod]
            .groupby("annee", as_index=False)
            .agg(ca=("ca", "sum"), quantite=("quantite", "sum"))
        )
        if not p.empty:
            fig1 = px.bar(p, x="annee", y="ca", title=f"CA par année — {sel_prod}")
            fig2 = px.line(
                p,
                x="annee",
                y="quantite",
                markers=True,
                title=f"Quantités par année — {sel_prod}",
            )
            st.plotly_chart(fig1, use_container_width=True)
            st.plotly_chart(fig2, use_container_width=True)

# ---- Analyse des prix ---- #
with tab_prices:
    c1, c2 = st.columns(2)
    # Histogramme prix
    if fdf["prix"].notna().sum() > 0:
        hist = px.histogram(
            fdf, x="prix", nbins=40, title="Distribution du champ 'prix'"
        )
        c1.plotly_chart(hist, use_container_width=True)
    # Boxplot prix par type
    if fdf["type_produit"].nunique() > 0:
        box = px.box(
            fdf,
            x="type_produit",
            y="prix",
            points="outliers",
            title="Prix par type de produit",
        )
        c2.plotly_chart(box, use_container_width=True)
    # Scatter prix vs quantite
    if fdf["quantite"].notna().sum() > 0:
        sc = px.scatter(
            fdf,
            x="quantite",
            y="prix",
            color="type_produit",
            title="Prix vs Quantité",
            hover_data=["nom_produit", "annee", "vecteur_id"],
        )
        st.plotly_chart(sc, use_container_width=True)

# ---- Table + export ---- #
with tab_table:
    st.write("Données filtrées")
    st.dataframe(fdf, use_container_width=True, height=480)
    csv_buf = io.StringIO()
    fdf.to_csv(csv_buf, index=False)
    st.download_button(
        "Télécharger (CSV)",
        csv_buf.getvalue(),
        file_name="export_filtre.csv",
        mime="text/csv",
    )
