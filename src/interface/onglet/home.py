import streamlit as st
import pandas as pd
import plotly.express as px
from src.utils.engineering import df_commande, df_stock


def render_home() -> None:
    df_c = df_commande()
    df_s = df_stock()
    st.title("🏠 Accueil — Chavost")
    st.markdown(
        """
Bienvenue sur le **tableau de bord ventes** de Chavost.

**Ce que vous pouvez faire :**
- Explorer vos ventes par **année**, **type**, **produit**, **pays**.
- Suivre vos **clients** (numéro aujourd'hui, **nom** demain) et ajouter des ventes.
- Exporter des sous-ensembles de données et **gérer la base** facilement.
        """
    )
    st.markdown("---")
    # KPIs
    c1, c2 = st.columns(2)
    try:
        c1.metric("Commandes totales passées", (len(df_c)))
        # Les produit vendus aujourd'hui
        aujourdhui = pd.Timestamp.today().normalize()
        df_s_today = df_s[df_s["date"].dt.normalize() == aujourdhui]

        nb_articles_vendus = df_s_today["quantite_reel"].abs().sum()

        c2.metric("Quantité vendue aujourd’hui", int(nb_articles_vendus))
    except Exception as e:
        st.info(f"Aperçu indisponible : {e}")

    st.divider()

    # Quick actions
    st.subheader("Raccourcis")
    q1, q2, q3, q4 = st.columns(4)
    if q1.button("📊 Ouvrir — Vue d’ensemble", use_container_width=True):
        st.session_state.page = "Analyses:overview"
        st.rerun()
    if q2.button("🗺️ Ouvrir — Carte export", use_container_width=True):
        st.session_state.page = "Analyses:map"
        st.rerun()
    if q3.button("🧰 Ouvrir — Gestion base", use_container_width=True):
        st.session_state.page = "Outils:db"
        st.rerun()
    if q4.button("🍾 Ouvrir — Analyse des produits", use_container_width=True):
        st.session_state.page = "Analyses:product"
        st.rerun()

    # Mini trend par mois
    try:
        by_month = df_c.groupby(["mois_annee"], as_index=False)["net_payer"].sum()
        if not by_month.empty:
            fig = px.line(
                by_month,
                x="mois_annee",
                y="net_payer",
                markers=True,
                title="Tendance du prix total par mois",
            )
            st.plotly_chart(fig, use_container_width=True)
    except Exception:
        pass
    # Top 5 des bouteilles les plus vendues
    try:
        bout = (
            df_s.groupby(["article"], as_index=False)["quantite_reel"]
            .sum()
            .sort_values("quantite_reel", ascending=False)
            .head(5)
        )
        if not bout.empty:
            fig_bout = px.bar(
                bout,
                x="article",
                y="quantite_reel",
                title="Top 5 des bouteilles les plus vendues",
            )
            st.plotly_chart(fig_bout, use_container_width=True)
    except Exception:
        pass
    st.markdown("---")
    st.success("Meilleur ventes du mois")
    col_1, col_2 = st.columns(2)
    with col_1:
        # Ici on fait un encadré avec la meilleur vente du mois

        dernier_mois = df_s["date"].dt.to_period("M").max()
        df_s_last_month = df_s[df_s["date"].dt.to_period("M") == dernier_mois]
        best_sale_q = df_s_last_month.groupby("article")["quantite_reel"].sum()
        article_top_q = best_sale_q.idxmax()
        valeur_top_q = best_sale_q.max()
        col_1.metric(
            "Meilleure vente du mois en quantité",
            value=f"{valeur_top_q:,.2f} (bouteilles)",
        )
        col_1.caption(f"Article : **{article_top_q}**")

    with col_2:
        # Ici on fait un encadré avec la meilleur vente du mois

        dernier_mois = df_s["date"].dt.to_period("M").max()
        df_s_last_month = df_s[df_s["date"].dt.to_period("M") == dernier_mois]
        best_sale_p = df_s_last_month.groupby("article")["valeur_du_mouvement"].sum()
        article_top_p = best_sale_p.idxmax()
        valeur_top_p = best_sale_p.max()

        col_2.metric(
            "Meilleure vente du poix en prix d'achat", value=f"{valeur_top_p:,.2f} €"
        )
        col_2.caption(f"Article : **{article_top_p}**")

    st.markdown("---")
    st.error("Moins bonnes ventes du mois")

    col_1_, col_2_ = st.columns(2)
    with col_1:
        # Ici on fait un encadré avec la meilleur vente du mois

        dernier_mois = df_s["date"].dt.to_period("M").max()
        df_s_last_month = df_s[df_s["date"].dt.to_period("M") == dernier_mois]
        best_sale_q = df_s_last_month.groupby("article")["quantite_reel"].sum()
        article_top_q = best_sale_q.idxmin()
        valeur_top_q = best_sale_q.min()
        col_1_.metric(
            "Meilleure vente du mois en quantité",
            value=f"{valeur_top_q:,.2f} (bouteilles)",
        )
        col_1_.caption(f"Article : **{article_top_q}**")

    with col_2_:
        # Ici on fait un encadré avec la meilleur vente du mois

        dernier_mois = df_s["date"].dt.to_period("M").max()
        df_s_last_month = df_s[df_s["date"].dt.to_period("M") == dernier_mois]
        best_sale_p = df_s_last_month.groupby("article")["valeur_du_mouvement"].sum()
        article_top_p = best_sale_p.idxmin()
        valeur_top_p = best_sale_p.min()

        col_2_.metric(
            "Meilleure vente du poix en prix d'achat", value=f"{valeur_top_p:,.2f} €"
        )
        col_2_.caption(f"Article : **{article_top_q}**")


if __name__ == "__main__":
    render_home()
