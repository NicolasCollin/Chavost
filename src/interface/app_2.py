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

RUNTIME_KEY = "runtime_df"

## Ca on va juste modifier les choses principales genre tout les boutons mais on garde l'idée
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

#On garde le guide qui est bien
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

#On retire les filtres, car comme il y a beacoup de base, cela ne sert plus à rien.


#La on fera le squelette en fonciton des boutons qu'on va configurer

# et la on fait le main
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



