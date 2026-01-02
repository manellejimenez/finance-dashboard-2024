Ce projet est une plateforme interactive d'analyse financière développée en Python avec Streamlit. Elle permet d'analyser des actifs financiers, de tester des stratégies de trading et d'utiliser le Machine Learning pour la prédiction de prix.

Fonctionnalités : Module Quant A (Analyse Univariee)
Le module Quant A se concentre sur l'analyse d'un actif unique sélectionné dynamiquement via l'API Yahoo Finance.

Extraction de Donnees : Récupération automatique des prix historiques via yfinance.

Backtesting de Strategies :

Buy and Hold : Performance de référence (achat et conservation).

Momentum (SMA Cross) : Stratégie basée sur la moyenne mobile simple à 20 jours.

Indicateurs de Performance :

Calcul du Sharpe Ratio pour mesurer le rendement ajusté au risque.

Calcul du Max Drawdown pour évaluer la perte maximale historique.

Visualisation Interactive : Graphiques dynamiques avec Plotly.

Bonus : Machine Learning
Nous avons intégré un modèle de Régression Linéaire (scikit-learn) pour prédire la prochaine clôture de l'actif.

Méthodologie : Le modèle apprend sur les indices de temps et les prix de clôture passés pour extrapoler la tendance immédiate (Next-Day Prediction).

Installation et Lancement
Cloner le projet : git clone https://github.com/manellejimenez/finance-dashboard-2024.git

Installer les dépendances : pip install -r requirements.txt

Lancer l'application : streamlit run app.py

Deploiement Linux et Automatisation
Serveur : Déployé sur une VM Linux (Ubuntu/Debian) accessible via SSH.

Persistance : Utilisation de tmux pour maintenir le serveur Streamlit actif 24h/24.

Rapports : Automatisation d'un script daily_report.py via une tâche Cron à 20h00 chaque jour.# finance-dashboard-2024
