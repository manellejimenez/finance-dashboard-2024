import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from datetime import timedelta

def run():
    st.header("Module Quant A: Analyse Univariee et Strategies")

    # --- 1. CONTROLES INTERACTIFS (SIDEBAR) ---
    st.sidebar.subheader("Parametres de l'Actif")
    
    # Choix de l'actif [cite: 32]
    asset = st.sidebar.selectbox(
        "Selectionner un actif", 
        ["AAPL", "MSFT", "TSLA", "EURUSD=X", "GC=F", "BTC-USD", "^GSPC"]
    )

    # Choix de la periodicite (Instruction: interactive controls) 
    period = st.sidebar.selectbox(
        "Historique des donnees", 
        ["3mo", "6mo", "1y", "2y", "5y", "max"], 
        index=2
    )

    st.sidebar.subheader("Parametres de la Strategie")
    strategy_type = st.sidebar.radio("Type de Strategie", ["Buy and Hold", "Moyenne Mobile (SMA)"])
    
    # Parametre dynamique pour la SMA (Instruction: strategy parameters) 
    sma_window = 20
    if strategy_type == "Moyenne Mobile (SMA)":
        sma_window = st.sidebar.slider("Fenetre SMA (Jours)", min_value=5, max_value=200, value=20)

    # --- 2. RECUPERATION ET NETTOYAGE DES DONNEES ---
    try:
        # Telechargement dynamique [cite: 15]
        data = yf.download(asset, period=period, interval="1d", progress=False)
        
        if data.empty:
            st.error(f"Aucune donnee disponible pour {asset}. Verifiez votre connexion ou le symbole.")
            return

        # Gestion du MultiIndex (bug frequent yfinance)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # Affichage du prix en temps reel [cite: 19]
        last_price = float(data['Close'].iloc[-1])
        prev_price = float(data['Close'].iloc[-2])
        variation = (last_price - prev_price) / prev_price
        
        col_metric1, col_metric2 = st.columns(2)
        col_metric1.metric(f"Prix Actuel ({asset})", f"{last_price:.2f}", f"{variation:.2%}")

        # --- 3. IMPLEMENTATION DES STRATEGIES ---
        # Calcul des rendements quotidiens
        data['Returns'] = data['Close'].pct_change()

        # Logique des strategies [cite: 33]
        if strategy_type == "Buy and Hold":
            data['Signal'] = 1 # Toujours investi
        else:
            # Strategie Momentum simple : Prix > SMA
            data['SMA'] = data['Close'].rolling(window=sma_window).mean()
            data['Signal'] = np.where(data['Close'] > data['SMA'], 1, 0)

        # Calcul de la performance de la strategie (Decalage d'un jour pour eviter le biais du futur)
        data['Strategy_Returns'] = data['Signal'].shift(1) * data['Returns']

        # Normalisation Base 100 pour comparaison professionnelle
        data['Cumulative_Market'] = 100 * (1 + data['Returns'].fillna(0)).cumprod()
        data['Cumulative_Strategy'] = 100 * (1 + data['Strategy_Returns'].fillna(0)).cumprod()

        # --- 4. CALCUL DES METRIQUES ---
        # Sharpe Ratio (Annualise)
        if data['Strategy_Returns'].std() != 0:
            sharpe_ratio = (data['Strategy_Returns'].mean() / data['Strategy_Returns'].std()) * np.sqrt(252)
        else:
            sharpe_ratio = 0
            
        # Max Drawdown 
        rolling_max = data['Cumulative_Strategy'].cummax()
        drawdown = (data['Cumulative_Strategy'] - rolling_max) / rolling_max
        max_drawdown = drawdown.min()

        # Affichage propre des metriques
        col_metric2.metric("Sharpe Ratio (Annuel)", f"{sharpe_ratio:.2f}")
        col_metric1.metric("Max Drawdown", f"{max_drawdown:.2%}")

        # --- 5. VISUALISATION GRAPHIQUE (PLOTLY) ---
        # Graphique principal combinant prix brut et strategie 
        fig = go.Figure()

        # Courbe 1 : L'actif (Benchmark)
        fig.add_trace(go.Scatter(
            x=data.index, 
            y=data['Cumulative_Market'], 
            name=f"Performance {asset} (Buy & Hold)",
            line=dict(color='gray', width=1.5),
            opacity=0.7
        ))

        # Courbe 2 : La strategie (Mise en valeur)
        fig.add_trace(go.Scatter(
            x=data.index, 
            y=data['Cumulative_Strategy'], 
            name=f"Strategie {strategy_type}",
            line=dict(color='#00CC96', width=2.5) # Vert professionnel
        ))

        fig.update_layout(
            title="Comparaison de Performance (Base 100)",
            xaxis_title="Date",
            yaxis_title="Valeur du Portefeuille",
            template="plotly_white", # Fond blanc plus propre pour les rapports
            hovermode="x unified",
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
            margin=dict(l=0, r=0, t=40, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

        # --- 6. BONUS : MACHINE LEARNING (PREDICTION) ---
        st.subheader("Modele Predictif (Regression Lineaire)")
        st.write("Estimation de la tendance a court terme basee sur l'historique recent.")

        # Preparation des donnees pour ML 
        df_ml = data[['Close']].dropna().tail(60) # On utilise les 60 derniers jours pour la tendance locale
        df_ml['Index'] = np.arange(len(df_ml))
        
        X = df_ml[['Index']]
        y = df_ml['Close']
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Prediction J+1
        next_index = [[len(df_ml)]]
        prediction = model.predict(next_index)[0]
        
        # Affichage du resultat
        delta_pred = (prediction - last_price) / last_price
        direction = "haussiere" if delta_pred > 0 else "baissiere"
        
        st.info(f"Prediction du modele pour la prochaine cloture : {prediction:.2f} ({delta_pred:+.2%}). Tendance {direction}.")

    except Exception as e:
        st.error(f"Une erreur technique est survenue : {e}")

if __name__ == "__main__":
    run()