import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px

def run():
    st.header("Module Quant B : Analyse de Portefeuille")

    # 1. Configuration du portefeuille
    assets = st.multiselect(
        "Sélectionnez les actifs du portefeuille",
        ["AAPL", "MSFT", "TSLA", "GOOGL", "AMZN", "BTC-USD"],
        default=["AAPL", "MSFT", "TSLA"]
    )

    if not assets:
        st.warning("Veuillez sélectionner au moins un actif.")
        return

    try:
        # 2. Récupération des données
        data = yf.download(assets, period="1y")['Close']
        
        # Nettoyage si MultiIndex
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # 3. Calcul des rendements et corrélation
        returns = data.pct_change().dropna()
        
        st.subheader("Matrice de Corrélation")
        corr_matrix = returns.corr()
        fig_corr = px.imshow(corr_matrix, text_auto=True, aspect="auto", color_continuous_scale='RdBu_r')
        st.plotly_chart(fig_corr)

        # 4. Optimisation simple (Poids égaux)
        st.subheader("Performance du Portefeuille (Equipondéré)")
        weights = np.array([1/len(assets)] * len(assets))
        portfolio_returns = returns.dot(weights)
        cumulative_returns = (1 + portfolio_returns).cumprod()

        # 5. Comparaison Graphique
        fig_perf = px.line(cumulative_returns, title="Evolution de la valeur du portefeuille (Base 1)")
        st.plotly_chart(fig_perf)

        # 6. Métriques du Portefeuille
        volatility = portfolio_returns.std() * np.sqrt(252)
        total_return = (cumulative_returns.iloc[-1] - 1)
        
        col1, col2 = st.columns(2)
        col1.metric("Volatilité Annuelle", f"{volatility:.2%}")
        col2.metric("Rendement Total (1an)", f"{total_return:.2%}")

    except Exception as e:
        st.error(f"Erreur dans le module Quant B : {e}")

if __name__ == "__main__":
    run()