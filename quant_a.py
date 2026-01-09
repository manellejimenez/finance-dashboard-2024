import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression


def run():
    st.header("Module Quant A : Analyse Univariée et Stratégies")

    # --- 1. CONTROLES INTERACTIFS ---
    st.sidebar.subheader("Paramètres de l'Actif")

    asset = st.sidebar.selectbox(
        "Sélectionner un actif",
        ["AAPL", "MSFT", "TSLA", "EURUSD=X", "GC=F", "BTC-USD", "^GSPC"]
    )

    period = st.sidebar.selectbox(
        "Historique des données",
        ["3mo", "6mo", "1y", "2y", "5y", "max"],
        index=2
    )

    st.sidebar.subheader("Paramètres de la Stratégie")
    strategy_type = st.sidebar.radio(
        "Type de Stratégie",
        ["Buy and Hold", "Moyenne Mobile (SMA)"]
    )

    sma_window = 20
    if strategy_type == "Moyenne Mobile (SMA)":
        sma_window = st.sidebar.slider(
            "Fenêtre SMA (jours)",
            min_value=5,
            max_value=200,
            value=20
        )

    # --- 2. RECUPERATION DES DONNEES ---
    try:
        data = yf.download(asset, period=period, interval="1d", progress=False)

        if data.empty or len(data) < 2:
            st.error("Données insuffisantes pour l'analyse.")
            return

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        last_price = float(data["Close"].iloc[-1])
        prev_price = float(data["Close"].iloc[-2])
        variation = (last_price - prev_price) / prev_price

        col1, col2 = st.columns(2)
        col1.metric(f"Prix actuel ({asset})", f"{last_price:.2f}", f"{variation:.2%}")

        # --- 3. STRATEGIES ---
        data["Returns"] = data["Close"].pct_change()

        if strategy_type == "Buy and Hold":
            data["Signal"] = 1
        else:
            data["SMA"] = data["Close"].rolling(window=sma_window).mean()
            data["Signal"] = np.where(data["Close"] > data["SMA"], 1, 0)

        data["Strategy_Returns"] = data["Signal"].shift(1) * data["Returns"]

        data["Cumulative_Market"] = 100 * (1 + data["Returns"].fillna(0)).cumprod()
        data["Cumulative_Strategy"] = 100 * (1 + data["Strategy_Returns"].fillna(0)).cumprod()

        # --- 4. METRIQUES ---
        sr = data["Strategy_Returns"].dropna()
        sharpe_ratio = (sr.mean() / sr.std()) * np.sqrt(252) if sr.std() != 0 else np.nan

        rolling_max = data["Cumulative_Strategy"].cummax()
        drawdown = (data["Cumulative_Strategy"] - rolling_max) / rolling_max
        max_drawdown = drawdown.min()

        col2.metric("Sharpe Ratio (annuel)", f"{sharpe_ratio:.2f}")
        col1.metric("Max Drawdown", f"{max_drawdown:.2%}")

        # --- 5. VISUALISATION ---
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=data.index,
            y=data["Cumulative_Market"],
            name="Buy & Hold",
            line=dict(color="gray", width=1.5),
            opacity=0.7
        ))

        fig.add_trace(go.Scatter(
            x=data.index,
            y=data["Cumulative_Strategy"],
            name=f"Stratégie {strategy_type}",
            line=dict(color="#00CC96", width=2.5)
        ))

        fig.update_layout(
            title="Comparaison de Performance (Base 100)",
            xaxis_title="Date",
            yaxis_title="Valeur",
            template="plotly_white",
            hovermode="x unified",
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
        )

        st.plotly_chart(fig, use_container_width=True)

        # --- 6. BONUS ML ---
        st.subheader("Modèle Prédictif (Régression Linéaire)")

        df_ml = data[["Close"]].dropna().tail(60)
        df_ml["Index"] = np.arange(len(df_ml))

        X = df_ml[["Index"]]
        y = df_ml["Close"]

        model = LinearRegression()
        model.fit(X, y)

        prediction = model.predict([[len(df_ml)]])[0]
        delta_pred = (prediction - last_price) / last_price
        direction = "haussière" if delta_pred > 0 else "baissière"

        st.info(
            f"Prévision J+1 : {prediction:.2f} "
            f"({delta_pred:+.2%}) — tendance {direction}."
        )

    except Exception as e:
        st.error(f"Erreur technique dans le module Quant A : {e}")


if __name__ == "__main__":
    run()
