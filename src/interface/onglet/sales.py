import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def get_data():
   
    try:
        df_mouv = st.session_state.get('df_mouv_stock')
        df_articles = st.session_state.get('df_article_precis')
        df_histo = st.session_state.get('df_histo_clients')
        df_clients = st.session_state.get('df_client_prospect')
    except Exception as e:
        st.error(f"Erreur de chargement des données: {e}")
        return None

    return df_mouv, df_articles, df_histo, df_clients

def prepare_analysis_data(df_mouv, df_articles, df_histo, df_clients):
    """
    Merges the separated Excel files into one DataFrame for analysis.
    """
    # 1. Filter Movements
    df_sales = df_mouv.copy() 
    
    # 2. Merge with Articles to get Cuvées
    df_master = pd.merge(
        df_sales, 
        df_articles[['Code article', 'Libellé', 'Unité']], 
        on='Code article', 
        how='left'
    )
    
    # 3. Merge with History to get Client Type and Client Code
    histo_subset = df_histo[['N° document', 'Code client', 'Libellé famille', 'Nom du client']].drop_duplicates(subset='N° document')
    
    df_master = pd.merge(
        df_master,
        histo_subset,
        on='N° document',
        how='left'
    )

    # 4. Clean Data
    df_master['Date'] = pd.to_datetime(df_master['Date'])
    
    # Calculate Total Price for the line 
    
    return df_master

# Main page function
def render_sales_page():
    st.title("🍷 Analyse des Ventes")
    
    # 1. Load & Prep
    data_tuple = get_data()
    if not data_tuple or any(d is None for d in data_tuple):
        st.warning("Veuillez charger les fichiers Excel via la page d'accueil ou le login.")
        return

    df_mouv, df_articles, df_histo, df_clients = data_tuple
    
    # Cache the prep step for performance
    if 'df_master' not in st.session_state:
        st.session_state['df_master'] = prepare_analysis_data(df_mouv, df_articles, df_histo, df_clients)
    
    df = st.session_state['df_master']

    # Adding sidebar filters
    st.sidebar.header("Filtres")
    
    # Date Filter
    min_date = df['Date'].min()
    max_date = df['Date'].max()
    date_range = st.sidebar.date_input(
        "Période",
        value=(min_date, max_date)
    )
    
    # Filter Data based on date
    if len(date_range) == 2:
        mask = (df['Date'] >= pd.to_datetime(date_range[0])) & (df['Date'] <= pd.to_datetime(date_range[1]))
        df_filtered = df.loc[mask]
    else:
        df_filtered = df

    # KPI section 
    col1, col2, col3 = st.columns(3)
    
    total_revenue = df_filtered['Valeur du mouvement'].sum()
    total_bottles = df_filtered['Quantité'].sum() # Assuming 'Quantité' is bottles
    top_client = df_filtered.groupby('Nom du client')['Valeur du mouvement'].sum().idxmax()
    
    col1.metric("Chiffre d'Affaires (Période)", f"{total_revenue:,.0f} €")
    col2.metric("Bouteilles Vendues", f"{total_bottles:,.0f}")
    col3.metric("Meilleur Client", top_client)

    st.markdown("---")

    # --- TABS FOR ANALYSIS ---
    tab1, tab2, tab3, tab4 = st.tabs(["Types de Clients", "Cuvées & Produits", "Chronologie", "Pays (Export)"])

    # 1. Analysis of clients
    with tab1:
        st.subheader("Répartition par Type de Client")
        
        col_a, col_b = st.columns(2)
        
        # Pie Chart - Revenue by Client Family
        fig_client_type = px.pie(
            df_filtered, 
            values='Valeur du mouvement', 
            names='Libellé famille',
            title="CA par Famille de Client",
            hole=0.4
        )
        col_a.plotly_chart(fig_client_type, use_container_width=True)
        
        # Bar Chart: Top 10 Clients
        df_top_clients = df_filtered.groupby('Nom du client')['Valeur du mouvement'].sum().sort_values().tail(10)
        fig_top_clients = px.bar(
            df_top_clients, 
            orientation='h', 
            title="Top 10 Clients (CA)",
            labels={'value': 'Chiffre d\'affaires', 'Nom du client': 'Client'}
        )
        col_b.plotly_chart(fig_top_clients, use_container_width=True)

    # 2. Analysis of cuvées
    with tab2:
        st.subheader("Performance par Cuvée")
        
        # Group by Article Label
        df_prod = df_filtered.groupby('Libellé')[['Quantité', 'Valeur du mouvement']].sum().reset_index()
        df_prod = df_prod.sort_values(by='Quantité', ascending=False)
        
        fig_prod = px.bar(
            df_prod, 
            x='Libellé', 
            y='Quantité', 
            color='Valeur du mouvement',
            title="Volume de vente par Cuvée (Couleur = CA)",
            text_auto=True
        )
        st.plotly_chart(fig_prod, use_container_width=True)

    # 3. Time series analysis 
    with tab3:
        st.subheader("Évolution des Ventes")
        
        # Resample by Month ('M') or Week ('W')
        df_time = df_filtered.set_index('Date').resample('M')['Valeur du mouvement'].sum().reset_index()
        
        fig_time = px.line(
            df_time, 
            x='Date', 
            y='Valeur du mouvement', 
            markers=True,
            title="Évolution Mensuelle du CA"
        )
        st.plotly_chart(fig_time, use_container_width=True)

    # 4. Geography
    with tab4:
        st.subheader("Répartition Géographique")
        
        if 'Pays' in df_clients.columns:
            # If we successfully merged 'Pays' from client_prospect earlier
            pass 
        elif 'Pays' in df_filtered.columns:
             geo_col = 'Pays'
        else:
            st.warning("⚠️ La colonne 'Pays' n'a pas été trouvée dans les fichiers Excel listés.")
            st.info("Affichage des ventes par Client en attendant la configuration géographique.")
            geo_col = 'Nom du client'

        # Placeholder logic for map/chart
        if 'Pays' in df_filtered.columns:
            df_geo = df_filtered.groupby('Pays')['Valeur du mouvement'].sum().reset_index()
            fig_map = px.choropleth(
                df_geo,
                locations="Pays", 
                locationmode='country names',
                color="Valeur du mouvement",
                title="Carte des Ventes"
            )
            st.plotly_chart(fig_map, use_container_width=True)