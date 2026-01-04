import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

def run():
    st.header("Module Quant B: Gestion de Portefeuille Multi-Actifs")

    # --- 1. CONTROLES DU PORTEFEUILLE (SIDEBAR) ---
    st.sidebar.subheader("Univers d'Investissement")
    
    # Sélection des actifs (Au moins 3 selon la consigne)
    assets = st.sidebar.multiselect(
        "Composition du Portefeuille",
        ["AAPL", "MSFT", "TSLA", "GOOGL", "AMZN", "NVDA", "META", "BTC-USD", "GC=F", "EURUSD=X"],
        default=["AAPL", "MSFT", "TSLA", "GOOGL"]
    )

    # Choix de la période
    period = st.sidebar.selectbox(
        "Historique des données", 
        ["3mo", "6mo", "1y", "2y", "5y", "max"], 
        index=2
    )

    # Gestion des Pondérations (Custom Weights)
    st.sidebar.subheader("Strategie d'Allocation")
    weight_mode = st.sidebar.radio("Type de Ponderation", ["Equipondere (Equal Weight)", "Personnalise (Custom)"])
    
    weights = []
    if not assets:
        st.error("Veuillez selectionner au moins un actif pour commencer l'analyse.")
        return

    # Logique de pondération
    if weight_mode == "Equipondere (Equal Weight)":
        # Poids égaux : 1/N
        weights = [1.0 / len(assets)] * len(assets)
    else:
        st.sidebar.write("Définir les poids (Total doit être 100%)")
        raw_weights = []
        for asset in assets:
            # On demande un poids entre 0 et 100 pour chaque actif
            w = st.sidebar.number_input(f"Poids {asset} (%)", min_value=0.0, max_value=100.0, value=100.0/len(assets))
            raw_weights.append(w)
        
        # Normalisation automatique pour éviter les erreurs mathématiques (si la somme != 100)
        total_raw = sum(raw_weights)
        if total_raw == 0:
            weights = [1.0 / len(assets)] * len(assets)
        else:
            weights = [w / total_raw for w in raw_weights]

    # --- 2. RECUPERATION DES DONNEES ---
    try:
        # Téléchargement
        data = yf.download(assets, period=period, interval="1d", progress=False)['Close']
        
        # Gestion MultiIndex et données manquantes
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        
        data = data.dropna() # On supprime les lignes vides pour aligner les dates

        if data.empty:
            st.error("Erreur de récupération des données API.")
            return

        # --- 3. CALCULS DE PERFORMANCE ---
        # Rendements quotidiens
        returns = data.pct_change().dropna()

        # Calcul du rendement du portefeuille pondéré
        # Formule matricielle : (Returns x Weights)
        portfolio_returns = returns.dot(weights)

        # Construction des bases 100 (Cumulative Returns)
        # 1. Portefeuille
        portfolio_cumulative = 100 * (1 + portfolio_returns).cumprod()
        
        # 2. Actifs individuels (pour la comparaison)
        assets_cumulative = 100 * (1 + returns).cumprod()

        # --- 4. VISUALISATION PRINCIPALE (PERFORMANCE) ---
        st.subheader("Performance Comparee (Base 100)")
        
        fig_perf = go.Figure()

        # Trace pour chaque actif individuel (en gris/ternes pour le contexte)
        for asset in assets:
            fig_perf.add_trace(go.Scatter(
                x=assets_cumulative.index,
                y=assets_cumulative[asset],
                mode='lines',
                name=asset,
                line=dict(width=1, color='rgba(150, 150, 150, 0.5)'), # Gris semi-transparent
                opacity=0.6
            ))

        # Trace pour le Portefeuille Global (Mise en valeur)
        fig_perf.add_trace(go.Scatter(
            x=portfolio_cumulative.index,
            y=portfolio_cumulative,
            mode='lines',
            name='Portefeuille Global',
            line=dict(width=3, color='#0047AB') # Bleu Cobalt professionnel
        ))

        fig_perf.update_layout(
            title="Evolution de la valeur : Portefeuille vs Actifs",
            xaxis_title="Date",
            yaxis_title="Valeur (Base 100)",
            template="plotly_white",
            hovermode="x unified",
            xaxis=dict(range=[portfolio_cumulative.index.min(), portfolio_cumulative.index.max()]),
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
        )
        st.plotly_chart(fig_perf, use_container_width=True)

        # --- 5. ANALYSE DE RISQUE (CORRELATION) ---
        st.subheader("Matrice de Correlation et Diversification")
        st.write("Analyse des interactions entre les actifs. Une correlation faible indique une meilleure diversification.")
        
        corr_matrix = returns.corr()
        
        # Heatmap personnalisée
        fig_corr = go.Figure(data=go.Heatmap(
            z=corr_matrix,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu', # Rouge (Correlé) à Bleu (Inverse)
            zmin=-1, zmax=1,
            text=corr_matrix.round(2),
            texttemplate="%{text}",
            showscale=True
        ))
        
        fig_corr.update_layout(
            title="Heatmap de Correlation",
            template="plotly_white",
            height=500
        )
        st.plotly_chart(fig_corr, use_container_width=True)

        # --- 6. INDICATEURS CLES (METRIQUES) ---
        st.subheader("Metriques du Portefeuille")
        
        # Calculs annuels (Hypothèse 252 jours de bourse)
        annual_volatility = portfolio_returns.std() * np.sqrt(252)
        total_return = (portfolio_cumulative.iloc[-1] / 100) - 1
        sharpe_ratio = (portfolio_returns.mean() / portfolio_returns.std()) * np.sqrt(252)

        # Affichage en colonnes
        col1, col2, col3 = st.columns(3)
        col1.metric("Rendement Total", f"{total_return:.2%}")
        col2.metric("Volatilite Annuelle", f"{annual_volatility:.2%}")
        col3.metric("Ratio de Sharpe", f"{sharpe_ratio:.2f}")

    except Exception as e:
        st.error(f"Erreur technique dans le module B : {e}")

if __name__ == "__main__":
    run()