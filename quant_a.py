import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression

def run():
    st.header("Module Quant A : Analyse Univariee")

    # 1. Selection de l'actif
    asset = st.selectbox("Selectionner un actif", ["AAPL", "MSFT", "TSLA", "EURUSD=X", "GC=F"])

    try:
        # 2. Recuperation des donnees
        data = yf.download(asset, period="1y", interval="1d")
        
        if data.empty:
            st.error("Echec du telechargement des donnees.")
            return

        # Nettoyage des colonnes (YFinance peut renvoyer des MultiIndex)
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        # Affichage du dernier prix
        last_price = float(data['Close'].iloc[-1])
        st.metric(f"Dernier prix : {asset}", f"{last_price:.2f}")

        # 3. Strategies de Backtesting
        strategy_choice = st.radio("Strategie", ["Buy and Hold", "Momentum (SMA Cross)"])
        
        data['Returns'] = data['Close'].pct_change()

        if strategy_choice == "Buy and Hold":
            data['Strategy_Logic'] = 1
        else:
            data['SMA20'] = data['Close'].rolling(window=20).mean()
            data['Strategy_Logic'] = np.where(data['Close'] > data['SMA20'], 1, 0)

        # 4. Calcul des performances
        data['Strategy_Returns'] = data['Strategy_Logic'].shift(1) * data['Returns']
        data['Cumulative_Asset'] = (1 + data['Returns']).cumprod()
        data['Cumulative_Strategy'] = (1 + data['Strategy_Returns']).cumprod()

        # Metriques
        sharpe = (data['Strategy_Returns'].mean() / data['Strategy_Returns'].std()) * np.sqrt(252)
        drawdown = (data['Cumulative_Strategy'] / data['Cumulative_Strategy'].cummax()) - 1
        max_drawdown = drawdown.min()

        col1, col2 = st.columns(2)
        col1.metric("Sharpe Ratio", f"{sharpe:.2f}")
        col2.metric("Max Drawdown", f"{max_drawdown:.2%}")

        # 5. Graphique Plotly
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data['Cumulative_Asset'], name="Asset"))
        fig.add_trace(go.Scatter(x=data.index, y=data['Cumulative_Strategy'], name="Strategie"))
        fig.update_layout(title="Performance Relative", template="plotly_dark")
        st.plotly_chart(fig)

        # 6. Bonus : Machine Learning (Regression Lineaire)
        st.subheader("Prediction prochaine cloture (ML)")
        df_ml = data[['Close']].dropna()
        df_ml['Day_Index'] = np.arange(len(df_ml))
        
        X = df_ml[['Day_Index']]
        y = df_ml['Close']
        
        model = LinearRegression()
        model.fit(X, y)
        
        prediction = model.predict([[len(df_ml)]])[0]
        st.write(f"Prix predit pour demain : **{float(prediction):.2f}**")

    except Exception as e:
        st.error(f"Erreur technique : {e}")

if __name__ == "__main__":
    run()