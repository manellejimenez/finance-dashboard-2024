# Rapport Technique : Plateforme d'Analyse Quantitative et de Prediction Financiere

## 1. Introduction et Objectifs du Projet
Ce projet consiste en la conception et le deploiement d'une infrastructure d'analyse financiere integree. L'objectif est de fournir une interface decisionnelle permettant de traiter des donnees de marche en temps reel, d'evaluer la pertinence de strategies algorithmiques et d'anticiper les tendances via l'apprentissage automatique (Machine Learning).

**Membres du groupe :**
* Manelle JIMENEZ DEL PESO
* Fares KHADDOUDI

---

## 2. Module Quant A : Analyse Univariee et Algorithmes de Trading

Le module Quant A repose sur l'etude de series temporelles isolees. Il permet de confronter une gestion passive (Buy and Hold) a une gestion active basee sur le momentum.

### 2.1 Modelisation de la Strategie SMA
La strategie de Moyenne Mobile Simple (SMA) genere des signaux d'achat et de vente selon la regle suivante :
* **Signal d'achat** : $C_t > SMA_n(t)$
* **Signal de vente** : $C_t \leq SMA_n(t)$
*Où $C_t$ represente le prix de cloture a l'instant $t$ et $n$ la fenetre d'observation (par defaut 20 jours).*

### 2.2 Metriques de Performance et Gestion du Risque
Pour valider l'efficacite de l'algorithme, deux indicateurs cles sont calcules :

* **Ratio de Sharpe (Annualise)** : Il mesure l'exces de rendement par unite de risque (volatilite).
  $$S = \frac{E[R_p - R_f]}{\sigma_p} \times \sqrt{252}$$
* **Maximum Drawdown (MDD)** : Il represente la perte maximale subie par un investisseur entre un sommet et un creux.
  $$MDD = \frac{\text{Valeur Crête} - \text{Valeur Creuse}}{\text{Valeur Crête}}$$

> **#CAPTURE_1** : Inserez ici une capture d'ecran du graphique de performance du Module Quant A. On doit y voir la courbe de l'actif et celle de la strategie diverger, ainsi que les blocs de metriques (Sharpe et Drawdown) affiches par Streamlit.

---

## 3. Module Quant B : Analyse Multivariee et Gestion de Portefeuille

Ce module traite des problematiques de diversification et d'allocation d'actifs.

### 3.1 Allocation et Rendement Cumule
Le portefeuille est construit selon un vecteur de poids $W = [w_1, w_2, ..., w_n]$. Le rendement total du portefeuille est la somme ponderee des rendements individuels. La visualisation est normalisee sur une **Base 100** pour une lisibilite accrue.

### 3.2 Analyse des Co-mouvements (Correlation)
L'evaluation de la diversification repose sur la matrice de correlation de Pearson. Une correlation proche de 1 indique une redondance du risque, tandis qu'une correlation proche de 0 ou negative indique une diversification optimale.
$$\rho_{X,Y} = \frac{\text{cov}(X,Y)}{\sigma_X \sigma_Y}$$

> **#CAPTURE_2** : Inserez ici une capture d'ecran de la Heatmap de correlation du Module Quant B montrant les relations entre les actifs selectionnes (AAPL, TSLA, BTC, etc.).

---

## 4. Intelligence Artificielle et Modelisation Predictive

Le projet integre une brique de Machine Learning pour la prediction a court terme ($J+1$).

### 4.1 Regression Lineaire Simple
Le modele utilise une approche par moindres carres ordinaires (OLS) pour estimer la tendance future en se basant sur les 60 dernieres sessions de bourse.
$$y = \beta_0 + \beta_1 x + \epsilon$$

> **#CAPTURE_3** : Inserez ici une capture de la section Machine Learning en bas du module Quant A, affichant la prediction numerique du prix de cloture pour la session suivante.

---

## 5. Infrastructure Linux et Automatisation

Le deploiement a ete realise sur une instance serveur Linux, respectant les standards de production logicielle.

### 5.1 Persistance du Service
L'application Streamlit est executee au sein d'un multiplexeur de terminaux **tmux**. Cela garantit que le serveur reste operationnel independamment de l'etat de la connexion SSH locale de l'administrateur.

### 5.2 Automatisation des Taches (Cron)
Le script `daily_report.py` a ete configure dans le planificateur de taches **crontab** pour une execution automatique a 20h00 chaque jour.
```bash
# Configuration Cron
00 20 * * * /usr/bin/python3 /home/ubuntu/project/daily_report.py
