import streamlit as st 
import pandas as pd
from src.utils.engineering import df_article, df_commande, df_clients, df_stock, df_client_prosp


def client_tool():
    st.markdown("---")
    st.title("👥 Explorateur de client")
    st.markdown(
        """
Bienvenue sur **L'explorateur de clients** de Chavost.
"""
    )
    df =  df_clients()
    
    