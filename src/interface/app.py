"""Chavost Dashboard — Streamlit App with simple auth gate.
This module defines the Streamlit UI and a minimal in-app authentication.
"""

import io

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from src.utils.main_engineering import check_data
from src.interface.home import render_home

# =============================================================================
# Page metadata / Theme
# =============================================================================
st.set_page_config(page_title="Chavost — Tableau de bord", layout="wide")
st.markdown(
    """
    <style>
        /* Make sidebar a bit wider and full-height, reduce inner padding */
        [data-testid="stSidebar"] {
            width: 320px !important;
        }
        [data-testid="stSidebar"] > div:first-child {
            padding-top: 0.75rem !important;
        }
        /* Bring main container higher to align with sidebar */
        .block-container { padding-top: 0.75rem; }
        /* Nicer headings in sidebar */
        .sidebar-title { font-weight: 700; font-size: 1.1rem; margin-bottom: 0.5rem; }
        .sidebar-subtitle { font-weight: 600; font-size: 0.95rem; margin-top: 0.75rem; }
    </style>
    """,
    unsafe_allow_html=True,
)
# --- Extra CSS for sidebar refinement (rounded containers, button spacing) ---
st.markdown(
    """
    <style>
      /* Sidebar containers */
      section[data-testid="stSidebar"] .st-emotion-cache-1r6slb0, /* Streamlit >=1.36 fallback */
      section[data-testid="stSidebar"] .st-emotion-cache-13ln4jf { /* older */
        border-radius: 12px;
      }
      /* Buttons spacing */
      [data-testid="baseButton-secondary"], [data-testid="baseButton-primary"] {
        margin-bottom: 0.35rem;
      }
    </style>
    """,
    unsafe_allow_html=True,
)
px.defaults.template = "plotly_white"
BRAND_COLORS = px.colors.qualitative.Set2

# ----------------------------- Simple Auth ----------------------------------


def auth_gate() -> bool:
    """Very simple in-app authentication.
    Current credentials: login = "admin", password = "admin".
    Stores state in st.session_state['auth_ok'].
    """
    if "auth_ok" not in st.session_state:
        st.session_state["auth_ok"] = False

    # Already authenticated
    if st.session_state["auth_ok"]:
        # Sidebar logout
        with st.sidebar:
            st.markdown(
                "<div class='sidebar-title'>👤 Session</div>", unsafe_allow_html=True
            )
            if st.button("Se déconnecter", use_container_width=True):
                st.session_state["auth_ok"] = False
                # Scrub any runtime data on logout for confidentiality
                st.session_state.pop(RUNTIME_KEY, None)
                st.cache_data.clear()
                st.rerun()
        return True

    # Login form (centered)
    st.title("🔐 Connexion requise")
    st.write("Cette application est privée. Veuillez vous authentifier pour continuer.")
    with st.form("login_form", clear_on_submit=False):
        user = st.text_input("Identifiant", value="", placeholder="")
        pwd = st.text_input("Mot de passe", type="password", value="")
        submitted = st.form_submit_button("Se connecter")
        if submitted:
            if user == "admin" and pwd == "admin":
                st.session_state["auth_ok"] = True
                st.success("Connexion réussie. Redirection…")
                st.rerun()
            else:
                st.error("Identifiants invalides. Essayez à nouveau.")

    st.caption(
        "Astuce : les identifiants par défaut sont *admin / admin*. Pensez à les changer rapidement."
    )
    return False

    # Login form (centered)
    st.title("🔐 Connexion requise")
    st.write("Cette application est privée. Veuillez vous authentifier pour continuer.")
    with st.form("login_form", clear_on_submit=False):
        user = st.text_input("Identifiant", value="", placeholder="admin")
        pwd = st.text_input("Mot de passe", type="password", value="")
        submitted = st.form_submit_button("Se connecter")
        if submitted:
            if user == "admin" and pwd == "admin":
                st.session_state["auth_ok"] = True
                st.success("Connexion réussie. Redirection…")
                st.rerun()
            else:
                st.error("Identifiants invalides. Essayez à nouveau.")

    st.caption(
        "Astuce : les identifiants par défaut sont *admin / admin*. Pensez à les changer rapidement."
    )
    return False


# ----------------------------- Sidebar Navigation ---------------------------
def render_sidebar():
    """Sophisticated sidebar with grouped icon buttons and active highlight.
    Returns the selected page key and syncs st.session_state.page.
    """

    # Helper to draw a nav button with active state
    def nav_btn(
        label: str, page_key: str, *, icon: str = "", help: str | None = None
    ) -> None:
        active = st.session_state.page == page_key
        btn_label = f"{icon}  {label}" if icon else label
        # Primary style when active, secondary otherwise
        if st.button(
            btn_label,
            use_container_width=True,
            type=("primary" if active else "secondary"),
            key=f"nav_{page_key}",
            help=help,
        ):
            st.session_state.page = page_key
            st.rerun()

    with st.sidebar:
        # Sidebar header
        st.markdown(
            "<div class='sidebar-title'>🧭 Navigation</div>", unsafe_allow_html=True
        )
        if "page" not in st.session_state:
            st.session_state.page = "Accueil"

        # ACCUEIL
        with st.container(border=True):
            nav_btn(
                "Accueil",
                "Accueil",
                icon="🏠",
                help="Page d'introduction et raccourcis",
            )

        st.markdown(
            "<div class='sidebar-subtitle'>Analyses</div>", unsafe_allow_html=True
        )
        with st.container(border=True):
            nav_btn("Vue d’ensemble", "Analyses:overview", icon="📊")
            nav_btn("Évolution", "Analyses:time", icon="📈")
            nav_btn("Types & clients", "Analyses:types", icon="👥")
            nav_btn("Produits", "Analyses:products", icon="🧪")
            nav_btn("Carte export", "Analyses:map", icon="🗺️")
            nav_btn("Analyse des prix", "Analyses:prices", icon="💶")
            nav_btn("Table / Export", "Analyses:table", icon="📄")

        st.markdown(
            "<div class='sidebar-subtitle'>Outils</div>", unsafe_allow_html=True
        )
        with st.container(border=True):
            nav_btn("Explorateur client", "Outils:client", icon="🔎")
            nav_btn("Ajouter des ventes", "Outils:add", icon="➕")
            nav_btn("Gestion base", "Outils:db", icon="🧩")

        return st.session_state.page


def render_onboarding() -> None:
    st.title("Chavost — Tableau de bord ventes")
    with st.expander("🧭 Comment utiliser (guide rapide)", expanded=True):
        st.markdown(
            """
**Objectif.** Explorer rapidement les ventes par année, type de produit, client et produit.

**Étapes :**
1. Les données sont **chargées en mémoire** depuis un CSV importé par l'entreprise (confidentialité). Aucune sauvegarde automatique n'est faite côté serveur. Si aucun CSV n'est encore chargé, utilisez l'écran d'**import initial** ou **Outils → Gestion base**.
2. Filtrez par **Années**, **Types de produit**, **Clients (n°)** et recherchez un **produit**.
3. Parcourez les onglets : *Vue d’ensemble*, *Évolution*, *Types & clients*, *Produits*, *Carte export*, *Analyse des prix*, *Table / Export*.

**Glossaire**
- **Type de produit** : famille (ex. Champagne, Ratafia…)
- **Client** : identifiant client (numéro actuel = `vecteur_id`)
- **Prix total** : montant total de la vente
            """
        )


def build_filters(df: pd.DataFrame):
    """Render filters and return filtered dataframe + options (multi-product)."""
    with st.expander("🎛️ Filtres", expanded=True):
        years_all = [
            y for y in df["annee"].dropna().astype(int).sort_values().unique().tolist()
        ]
        years_all_str = [str(y) for y in years_all]
        sel_years = st.multiselect("Années", years_all_str, default=years_all_str)

        types_all = sorted(df["type_produit"].dropna().unique().tolist())
        sel_types = st.multiselect("Types de produit", types_all, default=types_all)

        # --- Sélection multiple de produits (saisie assistée intégrée) ---
        prod_all = sorted(df["nom_produit"].dropna().astype(str).unique().tolist())
        sel_products = st.multiselect(
            "Produits (sélection multiple)",
            options=prod_all,
            default=[],
            help="Tapez pour filtrer et sélectionnez un ou plusieurs produits. Laissez vide pour tous.",
        )

        top_n = st.slider("Top N produits", 3, 30, 10, step=1)

    mask = df["annee_str"].isin(sel_years) & df["type_produit"].isin(sel_types)
    if sel_products:
        mask &= df["nom_produit"].isin(sel_products)

    fdf = df.loc[mask].copy()
    if fdf.empty:
        st.warning("Aucune ligne avec ces filtres.")
        st.stop()
    return fdf, top_n


def render_quality_and_kpis(fdf: pd.DataFrame) -> None:
    with st.expander("🧪 Qualité des données (aperçu)"):
        dup_subset = [
            "annee",
            "type_produit",
            "nom_produit",
            "client",
            "quantite",
            "prix",
        ]
        nb_dup = int(fdf.duplicated(subset=dup_subset, keep=False).sum())
        miss_pct = fdf.isna().mean().round(3) * 100
        c1, c2, c3 = st.columns(3)
        c1.metric("Lignes filtrées", fmt_int(len(fdf)))
        c2.metric("Doublons potentiels", fmt_int(nb_dup))
        c3.metric(
            "Colonnes numériques",
            fmt_int(fdf.select_dtypes(include=[np.number]).shape[1]),
        )
        st.caption(
            "Doublons calculés sur (année, type_produit, nom_produit, client, quantite, prix)."
        )
        miss_top = miss_pct.sort_values(ascending=False).head(20)
        if not miss_top.empty:
            st.dataframe(miss_top.rename("missing_%"), use_container_width=True)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Lignes", fmt_int(len(fdf)))
    k2.metric("Produits distincts", fmt_int(fdf["nom_produit"].nunique()))
    k3.metric("Quantité totale", fmt_int(np.nansum(fdf["quantite"])))
    k4.metric("Prix total", fmt_int(np.nansum(fdf["prix_total"])))
    st.divider()


def render_analysis_tabs(fdf: pd.DataFrame, top_n: int, active: str) -> None:
    """Render only the selected analysis subsection (right-rail navigation)."""

    def section_overview():
        st.markdown("**Résumé visuel :** volumes et prix total par année et par type.")
        c1, c2 = st.columns([2, 1])
        by_year = fdf.groupby(["annee", "annee_str"], as_index=False).agg(
            prix_total=("prix_total", "sum"), qte=("quantite", "sum")
        )
        if not by_year.empty:
            fig = px.bar(
                by_year.sort_values("annee"),
                x="annee_str",
                y="prix_total",
                title="Prix total par année",
                color_discrete_sequence=BRAND_COLORS,
            )
            fig.update_layout(xaxis_title="Année", yaxis_title="Prix total")
            c1.plotly_chart(fig, use_container_width=True)

        by_type = (
            fdf.groupby("type_produit", as_index=False)["prix_total"]
            .sum()
            .sort_values("prix_total", ascending=False)
        )
        if not by_type.empty:
            total = by_type["prix_total"].sum()
            by_type["label"] = by_type.apply(
                lambda r: f"{r['type_produit']} — {100*r['prix_total']/total:.1f}%",
                axis=1,
            )
            pie = px.pie(
                by_type,
                names="label",
                values="prix_total",
                title="Répartition du prix total par type",
                color_discrete_sequence=BRAND_COLORS,
            )
            pie.update_traces(
                textinfo="percent",
                hovertemplate="%{label}<br>Prix total=%{value:,.0f}<extra></extra>",
            )
            c2.plotly_chart(pie, use_container_width=True)

    def section_time():
        st.markdown("**Tendances annuelles** — sélectionnez la métrique à tracer.")
        metric_choice = st.selectbox("Métrique", ["prix_total", "quantite"], index=0)
        by_year = fdf.groupby(["annee", "annee_str"], as_index=False).agg(
            prix_total=("prix_total", "sum"), qte=("quantite", "sum")
        )
        if not by_year.empty:
            line = px.line(
                by_year.sort_values("annee"),
                x="annee_str",
                y="prix_total" if metric_choice == "prix_total" else "qte",
                markers=True,
                title=f"Évolution de {metric_choice.replace('_', ' ').capitalize()}",
                color_discrete_sequence=BRAND_COLORS,
            )
            line.update_layout(
                xaxis_title="Année",
                yaxis_title=metric_choice.replace("_", " ").capitalize(),
            )
            st.plotly_chart(line, use_container_width=True)

        bt = fdf.groupby(["annee", "annee_str", "type_produit"], as_index=False)[
            "prix_total"
        ].sum()
        if not bt.empty:
            fig = px.bar(
                bt.sort_values("annee"),
                x="annee_str",
                y="prix_total",
                color="type_produit",
                barmode="group",
                title="Prix total par année et type",
                color_discrete_sequence=BRAND_COLORS,
            )
            fig.update_layout(xaxis_title="Année", yaxis_title="Prix total")
            st.plotly_chart(fig, use_container_width=True)

    def section_types():
        st.markdown("**Comparatif par familles et par clients.**")
        c1, c2 = st.columns(2)
        by_type = (
            fdf.groupby("type_produit", as_index=False)["prix_total"]
            .sum()
            .sort_values("prix_total", ascending=False)
        )
        if not by_type.empty:
            bar_t = px.bar(
                by_type,
                x="type_produit",
                y="prix_total",
                title="Prix total par type de produit",
                color_discrete_sequence=BRAND_COLORS,
            )
            bar_t.update_layout(xaxis_title="Type", yaxis_title="Prix total")
            c1.plotly_chart(bar_t, use_container_width=True)

        by_client = (
            fdf.groupby("client", as_index=False)["prix_total"]
            .sum()
            .sort_values("prix_total", ascending=False)
        )
        if not by_client.empty:
            bar_c = px.bar(
                by_client,
                x="client",
                y="prix_total",
                title="Prix total par client",
                color_discrete_sequence=BRAND_COLORS,
            )
            bar_c.update_layout(xaxis_title="Client", yaxis_title="Prix total")
            c2.plotly_chart(bar_c, use_container_width=True)

    def section_products():
        st.markdown("**Top produits et analyse détaillée par produit.**")
        top_prix = (
            fdf.groupby("nom_produit", as_index=False)
            .agg(prix_total=("prix_total", "sum"), quantite=("quantite", "sum"))
            .sort_values("prix_total", ascending=False)
            .head(top_n)
        )
        c1, c2 = st.columns(2)
        if not top_prix.empty:
            bar_top = px.bar(
                top_prix,
                x="nom_produit",
                y="prix_total",
                title=f"Top {top_n} produits — Prix total",
                color_discrete_sequence=BRAND_COLORS,
            )
            bar_top.update_layout(xaxis_title="Produit", yaxis_title="Prix total")
            c1.plotly_chart(bar_top, use_container_width=True)

            bar_q = px.bar(
                top_prix,
                x="nom_produit",
                y="quantite",
                title=f"Top {top_n} produits — Quantités",
                color_discrete_sequence=BRAND_COLORS,
            )
            bar_q.update_layout(xaxis_title="Produit", yaxis_title="Quantité")
            c2.plotly_chart(bar_q, use_container_width=True)

        prods = top_prix["nom_produit"].tolist() or sorted(
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
                .agg(prix_total=("prix_total", "sum"), quantite=("quantite", "sum"))
                .sort_values("annee")
            )
            if not p.empty:
                fig1 = px.bar(
                    p,
                    x="annee_str",
                    y="prix_total",
                    title=f"Prix total par année — {sel_prod}",
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

    def section_map():
        st.markdown("**Export par pays** — somme du prix total par pays.")
        by_country = (
            fdf.groupby("country", as_index=False)["prix_total"]
            .sum()
            .sort_values("prix_total", ascending=False)
        )
        if by_country.empty:
            st.info("Aucun pays disponible dans le filtre courant.")
        else:
            map_fig = px.choropleth(
                by_country,
                locations="country",
                locationmode="country names",
                color="prix_total",
                title="Carte des exportations (prix total)",
                color_continuous_scale="Blues",
            )
            map_fig.update_layout(margin=dict(l=0, r=0, t=60, b=0))
            st.plotly_chart(map_fig, use_container_width=True)
            st.dataframe(
                by_country.rename(columns={"prix_total": "prix_total_sum"}),
                use_container_width=True,
            )

    def section_prices():
        st.markdown(
            "**Structure des prix** — distribution, écarts et relation prix-quantité."
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
                hover_data=["nom_produit", "annee_str", "client"],
                color_discrete_sequence=BRAND_COLORS,
            )
            st.plotly_chart(sc, use_container_width=True)

    def section_table():
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

    sections = {
        "Vue d’ensemble": section_overview,
        "Évolution": section_time,
        "Types & clients": section_types,
        "Produits": section_products,
        "Carte export": section_map,
        "Analyse des prix": section_prices,
        "Table / Export": section_table,
    }
    sections.get(active, section_overview)()


def render_tools(df: pd.DataFrame, active_tool: str):
    def tool_client_explorer():
        st.markdown(
            "Explorez un client par **numéro (vecteur_id)** ou **nom**. La saisie déclenche la recherche automatiquement."
        )

        q = st.text_input(
            "Nom du client",
            key="client_query",
            placeholder="Exemples : Dupont, Michel...",
        )

        vid, label, many = _resolve_client(df, q)

        if many:
            st.caption("Plusieurs correspondances :")
            options = [f"{vid} — {lab}" for vid, lab in many]
            choice = st.selectbox("Sélectionnez un client", options)
            vid = choice.split(" — ", 1)[0]
            label = choice.split(" — ", 1)[1]

        if not vid:
            if q.strip():
                st.warning(
                    "Aucun client correspondant. Essayez un autre nom/identifiant."
                )
            return

        # --- Historique & KPIs (filter by vecteur_id ONLY) ---
        sdf = df.loc[df["vecteur_id"].astype(str) == str(vid)].copy()

        if sdf.empty:
            st.info(
                "Aucun historique pour ce client. Vous pouvez **ajouter une vente** ci‑dessous."
            )
            return

        display_name = label if label and label.strip() else str(vid)
        st.success(f"Client reconnu : **{display_name}** (vecteur_id = {vid})")
        # Memorize selection for prefill in "Ajouter des ventes"
        st.session_state["selected_client_id"] = str(vid)
        st.session_state["selected_client_label"] = str(display_name)

        # Shortcut to add a sale for this client
        add_col1, add_col2 = st.columns([1, 4])
        with add_col1:
            if st.button(
                "➕ Ajouter une vente pour ce client",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.page = "Outils:add"
                st.rerun()

        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("Commandes", fmt_int(len(sdf)))
        c2.metric("Années", fmt_int(sdf["annee"].nunique()))
        c3.metric("Produits", fmt_int(sdf["nom_produit"].nunique()))
        c4.metric("Quantité", fmt_int(float(sdf["quantite"].sum())))
        c5.metric("Prix total", fmt_int(float(sdf["prix_total"].sum())))
        c6.metric("Pays", fmt_int(sdf["country"].nunique()))

        st.divider()

        by_cty = (
            sdf.groupby("country", as_index=False)["prix_total"]
            .sum()
            .sort_values("prix_total", ascending=False)
        )
        cta, ctb = st.columns([1.2, 1.8])
        with cta:
            st.markdown("**Pays d’export**")
            st.dataframe(by_cty, use_container_width=True, height=260)
        with ctb:
            if not by_cty.empty:
                map_fig = px.choropleth(
                    by_cty,
                    locations="country",
                    locationmode="country names",
                    color="prix_total",
                    title=f"Carte des exportations — {display_name}",
                    color_continuous_scale="Blues",
                )
                map_fig.update_layout(margin=dict(l=0, r=0, t=60, b=0))
                st.plotly_chart(map_fig, use_container_width=True)

        by_y = (
            sdf.groupby(["annee", "annee_str"], as_index=False)["prix_total"]
            .sum()
            .sort_values("annee")
        )
        if not by_y.empty:
            fig = px.line(
                by_y,
                x="annee_str",
                y="prix_total",
                markers=True,
                title=f"Évolution — {display_name}",
            )
            st.plotly_chart(fig, use_container_width=True)

        left, right = st.columns(2)
        by_prod = (
            sdf.groupby("nom_produit", as_index=False)
            .agg(prix_total=("prix_total", "sum"), quantite=("quantite", "sum"))
            .sort_values("prix_total", ascending=False)
            .head(15)
        )
        if not by_prod.empty:
            left.plotly_chart(
                px.bar(
                    by_prod,
                    x="nom_produit",
                    y="prix_total",
                    title="Top produits — prix total",
                ),
                use_container_width=True,
            )
        by_type = (
            sdf.groupby("type_produit", as_index=False)["prix_total"]
            .sum()
            .sort_values("prix_total", ascending=False)
        )
        if not by_type.empty:
            right.plotly_chart(
                px.bar(
                    by_type,
                    x="type_produit",
                    y="prix_total",
                    title="Répartition par type",
                ),
                use_container_width=True,
            )

        st.markdown("**Commandes**")
        st.dataframe(
            sdf.sort_values(["annee", "nom_produit"]).reset_index(drop=True),
            use_container_width=True,
            height=380,
        )

    def tool_add():
        st.markdown(
            "**Ajouter des ventes (multi‑lignes)** — saisissez plusieurs produits avec quantités et prix, puis enregistrez en une fois."
        )

        # Prefill from client explorer if available
        prefill_id = st.session_state.get("selected_client_id", "")
        prefill_label = st.session_state.get("selected_client_label", "")
        if prefill_id:
            st.info(
                f"Client pré‑sélectionné : **{prefill_label or prefill_id}** (vecteur_id = {prefill_id})."
            )
            clear_prefill = st.button(
                "Effacer la présélection client", key="clear_prefill"
            )
            if clear_prefill:
                st.session_state.pop("selected_client_id", None)
                st.session_state.pop("selected_client_label", None)
                st.rerun()

        # Sources d'options (suggestions)
        type_options = sorted(df["type_produit"].dropna().astype(str).unique().tolist())
        prod_options = sorted(df["nom_produit"].dropna().astype(str).unique().tolist())
        # Liste de pays élargie : pays du fichier ∪ pays du dataset gapminder (Plotly)
        try:
            gap_countries = sorted(px.data.gapminder()["country"].unique().tolist())
        except Exception:
            gap_countries = []
        country_options = sorted(
            set(gap_countries)
            | set(df["country"].dropna().astype(str).unique().tolist())
        )

        # Valeurs par défaut
        default_year = int(df["annee"].dropna().max()) if not df.empty else 2024

        # Gabarit d'une ligne à saisir
        seed = pd.DataFrame(
            [
                {
                    "annee": default_year,
                    "type_produit": type_options[0] if type_options else "",
                    "nom_produit": prod_options[0] if prod_options else "",
                    "quantite": 0.0,
                    "prix": 0.0,
                    "client_input": str(prefill_id)
                    if prefill_id
                    else "",  # id client (vecteur_id) ou nom (client_name futur)
                    "country": "France"
                    if "France" in country_options
                    else (country_options[0] if country_options else "France"),
                }
            ]
        )

        st.caption(
            "Astuce : utilisez le bouton **+** pour ajouter des lignes. Les menus sont filtrables au clavier."
        )
        edited = st.data_editor(
            seed,
            num_rows="dynamic",
            use_container_width=True,
            height=360,
            column_config={
                "annee": st.column_config.NumberColumn(
                    "Année", min_value=1900, max_value=2100, step=1
                ),
                "type_produit": st.column_config.SelectboxColumn(
                    "Type de produit",
                    options=type_options,
                    help="Commencez à taper pour filtrer — vous pouvez aussi laisser vide et saisir plus tard.",
                ),
                "nom_produit": st.column_config.SelectboxColumn(
                    "Nom du produit",
                    options=prod_options,
                    help="Sélectionnez ou tapez pour filtrer.",
                ),
                "quantite": st.column_config.NumberColumn(
                    "Quantité", min_value=0.0, step=1.0
                ),
                "prix": st.column_config.NumberColumn(
                    "Prix total", min_value=0.0, step=1.0
                ),
                "client_input": st.column_config.TextColumn(
                    "Client (identifiant ou nom)",
                    help="Saisissez l'identifiant (vecteur_id) actuel ou le nom du client (quand disponible).",
                ),
                "country": st.column_config.SelectboxColumn(
                    "Pays",
                    options=country_options,
                    help="Liste élargie — filtrable au clavier.",
                ),
            },
            key="add_sales_editor",
        )

        save = st.button("Enregistrer les lignes visibles", type="primary")
        if save:
            try:
                base_df = get_data().copy()
                base_df.columns = [c.strip().lower() for c in base_df.columns]
                has_client_name_col = "nom_client" in base_df.columns

                rows_to_add = []
                for _, r in edited.iterrows():
                    if (
                        str(r.get("nom_produit", "")).strip() == ""
                        and float(r.get("quantite", 0) or 0) == 0
                        and float(r.get("prix", 0) or 0) == 0
                    ):
                        continue
                    new_row = {
                        "annee": int(r.get("annee", default_year) or default_year),
                        "type_produit": str(r.get("type_produit", "")).strip(),
                        "nom_produit": str(r.get("nom_produit", "")).strip(),
                        "quantite": float(r.get("quantite", 0) or 0),
                        "prix": float(r.get("prix", 0) or 0),
                        "vecteur_id": str(r.get("client_input", "")).strip()
                        if not has_client_name_col
                        else "",
                        "country": str(r.get("country", "")).strip(),
                    }
                    if has_client_name_col:
                        new_row["nom_client"] = str(r.get("client_input", "")).strip()
                    for c in [
                        "annee",
                        "type_produit",
                        "nom_produit",
                        "quantite",
                        "prix",
                        "country",
                    ]:
                        if c not in base_df.columns:
                            raise ValueError(f"Colonne manquante dans le fichier : {c}")
                    rows_to_add.append(new_row)

                if not rows_to_add:
                    st.warning("Aucune ligne à enregistrer.")
                    return

                updated = pd.concat(
                    [base_df, pd.DataFrame(rows_to_add)], ignore_index=True
                )
                # Apply in memory only (confidential mode)
                st.session_state[RUNTIME_KEY] = _coerce_and_validate(updated)
                st.cache_data.clear()
                st.success(f"{len(rows_to_add)} ligne(s) ajoutée(s) en mémoire.")

                # Offer a download of the updated base (optional)
                buf2 = io.StringIO()
                st.session_state[RUNTIME_KEY].to_csv(buf2, index=False)
                st.download_button(
                    "Télécharger la base mise à jour (CSV)",
                    buf2.getvalue(),
                    file_name="base_mise_a_jour.csv",
                    mime="text/csv",
                )
            except Exception as e:
                st.error(f"Échec de l'enregistrement en mémoire : {e}")

    def tool_base():
        st.markdown(
            "🧩 **Gestion de la base de données** — visualisez, éditez, exportez, supprimez des lignes, rechargez la base."
        )
        st.subheader("Importer / remplacer la base (CSV)")
        up_replace = st.file_uploader(
            "Nouveau CSV (remplace la base courante)", type=["csv"], key="replace_csv"
        )
        if up_replace is not None and st.button(
            "Charger ce fichier en mémoire", key="btn_replace_csv"
        ):
            try:
                new_df = load_csv_safely(up_replace)
                new_df = _coerce_and_validate(new_df)
                st.session_state[RUNTIME_KEY] = new_df
                st.success("Base chargée en mémoire (non enregistrée sur le serveur).")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Échec du chargement : {e}")
        base_df = get_data().copy()
        base_df.columns = [c.strip().lower() for c in base_df.columns]
        edited = st.data_editor(
            base_df,
            use_container_width=True,
            num_rows="dynamic",
            height=500,
            key="data_editor",
        )
        c1, c2, c3 = st.columns(3)
        buf = io.StringIO()
        edited.to_csv(buf, index=False)
        c1.download_button(
            "Exporter CSV", buf.getvalue(), file_name="base_ventes.csv", mime="text/csv"
        )
        apply_mem = st.button("Appliquer les modifications en mémoire", key="apply_mem")
        if apply_mem:
            try:
                st.session_state[RUNTIME_KEY] = _coerce_and_validate(edited.copy())
                st.success("Modifications appliquées en mémoire.")
                st.cache_data.clear()
            except Exception as e:
                st.error(f"Impossible d'appliquer les modifications : {e}")
        delete_rows = c2.button("Supprimer lignes sélectionnées")
        refresh_btn = c3.button("Rafraîchir le cache")
        if delete_rows:
            st.warning(
                "Suppression : supprimez directement les lignes dans le tableau puis exportez/sauvegardez."
            )
        if refresh_btn:
            st.cache_data.clear()
            st.success("Cache rafraîchi. Rechargez la page pour voir les changements.")

    tools = {
        "Explorateur client": tool_client_explorer,
        "Ajouter des ventes": tool_add,
        "🧩 Gestion base": tool_base,
    }
    tools.get(active_tool, tool_client_explorer)()


# ----------------------------- Main -----------------------------------------
def main() -> None:
    # ---- AUTH FIRST ----
    if not auth_gate():
        return

    # vérification si l'utilisateur possède les bases de données requises
    check_data()

    page = render_sidebar()

    if page == "Accueil":
        render_home()
        return

    # Analyses routing
    if page.startswith("Analyses:"):
        render_onboarding()
        fdf, top_n = build_filters(df)
        render_quality_and_kpis(fdf)
        mapping = {
            "Analyses:overview": "Vue d'ensemble",
            "Analyses:time": "Évolution",
            "Analyses:types": "Types & clients",
            "Analyses:products": "Produits",
            "Analyses:map": "Carte export",
            "Analyses:prices": "Analyse des prix",
            "Analyses:table": "Table / Export",
        }
        render_analysis_tabs(fdf, top_n, mapping.get(page, "Vue d'ensemble"))
        return

    # Outils routing
    if page == "Outils:client":
        render_onboarding()
        render_tools(df, "Explorateur client")
    elif page == "Outils:add":
        render_onboarding()
        render_tools(df, "Ajouter des ventes")
    elif page == "Outils:db":
        render_onboarding()
        render_tools(df, "🧩 Gestion base")


if __name__ == "__main__":
    main()
