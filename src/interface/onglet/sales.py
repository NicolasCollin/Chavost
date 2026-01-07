import streamlit as st
import pandas as pd
import plotly.express as px

try:
    from src.utils.engineering import df_stock, df_article, df_clients
except ImportError:
    from src.utils.main_engineering import df_stock, df_article, df_clients

# Data loading
def get_and_prepare_data():
    """
    Loads data using the existing engineering functions and merges them
    using the cleaned column names (snake_case).
    """

    df_mouv = df_stock()      
    df_arts = df_article()    
    df_histo = df_clients()   

    # Filtering for sales
    df_master = df_mouv.copy()

    # Merging with articles
    if 'code_article' in df_master.columns and 'code_article' in df_arts.columns:
        df_master['code_article'] = df_master['code_article'].astype(str)
        df_arts['code_article'] = df_arts['code_article'].astype(str)

        df_master = pd.merge(
            df_master,
            df_arts[['code_article', 'libell_', 'unit_']], # libell_ comes from "Libellé"
            on='code_article',
            how='left'
        )
    
    # Merging with clients
    if 'n_document' in df_master.columns and 'n_document' in df_histo.columns:
        client_cols = ['n_document', 'code_client', 'libell_famille', 'nom_du_client']
        
        existing_cols = [c for c in client_cols if c in df_histo.columns]
        histo_subset = df_histo[existing_cols].drop_duplicates(subset='n_document')
        
        df_master = pd.merge(
            df_master,
            histo_subset,
            on='n_document',
            how='left'
        )

    if 'date' in df_master.columns:
        df_master['date'] = pd.to_datetime(df_master['date'])

    return df_master

# Main page
def render_sales_page():
    st.title("🍷 Analyse des Ventes")

    if 'sales_dashboard_data' not in st.session_state:
        try:
            with st.spinner("Chargement et structuration des données..."):
                st.session_state['sales_dashboard_data'] = get_and_prepare_data()
        except Exception as e:
            st.error(f"Erreur lors du chargement via engineering.py : {e}")
            return

    df = st.session_state['sales_dashboard_data']

    # sidebar filters
    with st.sidebar:
        st.header("Filtres")
        
        # Date Filter
        if 'date' in df.columns:
            min_d, max_d = df['date'].min(), df['date'].max()
            rng = st.date_input("Période", value=(min_d, max_d))
            if isinstance(rng, tuple) and len(rng) == 2:
                mask = (df['date'] >= pd.to_datetime(rng[0])) & (df['date'] <= pd.to_datetime(rng[1]))
                df_filtered = df.loc[mask]
            else:
                df_filtered = df
        else:
            df_filtered = df

    # 3. KPIs
    
    col_val = 'valeur_du_mouvement' if 'valeur_du_mouvement' in df_filtered.columns else None
    col_qty = 'quantite_reel' if 'quantite_reel' in df_filtered.columns else 'quantit_'
    col_client = 'nom_du_client' if 'nom_du_client' in df_filtered.columns else None

    c1, c2, c3 = st.columns(3)
    
    if col_val:
        turnover = df_filtered[col_val].sum()
        c1.metric("Chiffre d'Affaires", f"{turnover:,.0f} €")
    
    if col_qty and col_qty in df_filtered.columns:
        volume = df_filtered[col_qty].sum()
        c2.metric("Volume (Unités)", f"{volume:,.0f}")
        
    if col_client and col_val:
        try:
            best = df_filtered.groupby(col_client)[col_val].sum().idxmax()
            c3.metric("Meilleur Client", str(best))
        except:
            c3.metric("Meilleur Client", "-")

    st.markdown("---")

    # Tabs - different types of analyses
    tab1, tab2, tab3 = st.tabs(["Types de Clients", "Cuvées", "Chronologie"])

    # Tab 1: clients
    with tab1:
        col_a, col_b = st.columns(2)
        if 'libell_famille' in df_filtered.columns and col_val:
            fig_pie = px.pie(df_filtered, values=col_val, names='libell_famille', title="CA par Famille", hole=0.4)
            col_a.plotly_chart(fig_pie, use_container_width=True)
        
        # Bar Chart: Top Clients
        if col_client and col_val:
            top_cli = df_filtered.groupby(col_client)[col_val].sum().nlargest(10).sort_values(ascending=True)
            fig_bar = px.bar(top_cli, orientation='h', title="Top 10 Clients")
            col_b.plotly_chart(fig_bar, use_container_width=True)

    # Tab 2: products
    with tab2:
        col_prod_name = 'libell_' 
        if col_prod_name in df_filtered.columns and col_qty and col_val:
            df_prod = df_filtered.groupby(col_prod_name)[[col_qty, col_val]].sum().reset_index()
            df_prod = df_prod.sort_values(by=col_qty, ascending=False)
            
            fig_prod = px.bar(
                df_prod, 
                x=col_prod_name, 
                y=col_qty, 
                color=col_val, 
                title="Ventes par Cuvée (Couleur = CA)",
                labels={col_prod_name: "Produit", col_qty: "Quantité", col_val: "CA (€)"}
            )
            st.plotly_chart(fig_prod, use_container_width=True)

    # Tab 3: chronology
    with tab3:
        if 'date' in df_filtered.columns and col_val:
            try:
                df_time = df_filtered.set_index('date').resample('ME')[col_val].sum().reset_index()
            except:
                df_time = df_filtered.set_index('date').resample('M')[col_val].sum().reset_index()
                
            fig_time = px.line(df_time, x='date', y=col_val, markers=True, title="Évolution Temporelle")
            st.plotly_chart(fig_time, use_container_width=True)