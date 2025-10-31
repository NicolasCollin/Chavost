# Chavost — Mission de consulting data (Coopérative Chavost)

## 1) Contexte

**Chavost** est une marque de champagne née au sein de la coopérative de **Chavot-Courcourt**. Une spécificité forte de la maison est la cuvée **sans sulfites ajoutés** (créée en 2019, commercialisée après 15 mois d’élevage). Cette approche implique un suivi œnologique plus fin (prévention de l’oxydation par gaz neutres, cuves inox hermétiques, contrôles rapprochés), et participe à un profil aromatique plus « pur ».  
Dans le même temps, la marque connaît une **croissance rapide** : des dizaines de milliers de bouteilles vendues la première année et **près de 100 000 de plus en 2024**. Cette montée en charge multiplie les **pays**, **importateurs**, **cuvées**, **formats** et **volumes stockés**, et rend critique la **structuration et l’exploitation** de la donnée commerciale.

---

## 2) Problématique

Les systèmes actuels ne permettent d’exploiter qu’une faible part de l’information disponible. Les questions métier sont nombreuses :  
- Comment évoluent les **ventes par pays**, par **importateur**, par **cuvée** et par **format** (75 cl, magnum, jéroboam, etc.) ?  
- Quelles **saisonnalités** (Noël, pics ponctuels) et quels **moments forts** stimuler (prévisions d’habillage, préparation des stocks) ?  
- Quels **prix moyens** et quelles **différences géographiques** observer ?  
- Comment mieux **piloter** la croissance avec des **indicateurs** clairs et un **outillage** accessible ?

---

## 3) Objectifs de la mission

1. **Créer la collaboration** et cadrer les besoins (entretiens, périmètre, planning).  
2. **Data Engineering** : transformer des **Excel bruts** (cellules fusionnées, totaux, mises en forme) en **base exploitable** (une ligne = une transaction).  
3. **Analytics & BI** : produire un **rapport BI** (Power BI) et une **interface** (Streamlit) pour explorer les ventes par pays/importateur/cuvée/format, suivre les tendances, et appuyer la décision.

---

## 4) Ce que fait le projet aujourd’hui

- **Nettoyage/structuration** des fichiers Excel hétérogènes.  
- **Construction d’une base tabulaire** avec les champs clefs (client, produit/cuvée, catégorie, format, année, quantité EQB, montant HT).  
- **Automatisation** du pipeline pour rejouer le traitement lors des mises à jour.  
- **Application Streamlit** pleinement implémentée, avec des tableaux de bord pour KPIs, tendances et filtres.  
- Préparation des livrables **Power BI** et **Streamlit** pour la suite du projet.

---

## 5) Arborescence du dépôt

```
chavost/
├── data/
│   └── base_cryptee.csv        # Jeu de données principal (CSV chiffré)
├── src/
│   ├── interface/              # Interface Streamlit principale
│   │   └── app.py
│   ├── tests/                  # Tests unitaires
│   │   └── test_main.py
│   └── utils/                  # Scripts utilitaires et fonctions
│       ├── __init__.py
│       ├── aliases.py
│       ├── fichier_R_2_engineer.R
│       └── main.py
├── .gitlab-ci.yml              # Pipeline CI/CD GitLab
├── .pre-commit-config.yaml     # Configuration du pré-commit
├── .python-version             # Version Python utilisée
├── pyproject.toml              # Dépendances et configuration uv
├── README.md                   # Documentation principale
└── uv.lock                     # Verrouillage des dépendances
```

---

## 6) Installation et exécution (à partir d’un clone GitLab)

### Prérequis
- **Python 3.13** recommandé
- **uv** (gestion d’environnement et exécution rapide) : https://docs.astral.sh/uv/
- Optionnel (pour la suite) : **Power BI Desktop** (Windows) et **Streamlit**

### 6.1 Cloner le dépôt

```bash
git clone https://gitlab-mi.univ-reims.fr/coll0155/chavost.git
cd chavost
```

### 6.2 Créer l’environnement et installer les dépendances

```bash
uv sync
```

### 6.3 Lancer l’application locale

```bash
uv run main
```

> Cette commande lance l’application Streamlit avec les tableaux de bord interactifs.

---

## 7) Stack technique

- **Python** (3.13), **Pandas** pour le traitement.  
- **uv** pour les environnements et l’exécution.  
- **Streamlit** pour l’interface utilisateur finalisée, avec des visualisations interactives basées sur **Plotly**.  
- **Power BI** pour le rapport BI (jalon BI finalisé).  
- Gestion de version **GitLab**, CI/CD en cours de préparation selon les besoins du client.

---

## 8) Roadmap synthétique

- **S1 — Cadrage** : entretiens, identification des besoins, planning.  
- **S2 — Data Eng.** : nettoyage Excel → base tabulaire, automatisation.  
- **S3 — BI** : construction du rapport Power BI (ventes par pays/importateur/cuvée/format, saisonnalité) — **terminé**.  
- **S4 — App** : interface Streamlit pour exploration dynamique et filtres — **complétée et en production**.  
- **S5 — Itérations** : retours client, priorisation des KPIs, mise en production graduelle — **en cours**.

---

## 9) Équipe & encadrement

- **Nikita POMOZOV** — Analyses & visualisations 
- **Nicolas COLLIN** — Développement & automatisation 
- **Matthis ARVOIS** — Data engineering & cadrage

Encadrement : **Emmanuelle GAUTHERAT** (Université de Reims Champagne-Ardenne).

---

## 10) Licence et statut

Projet académique dans le cadre du Master, destiné à un **usage interne** à la coopérative et à l’équipe pédagogique.  
**Statut** : en développement, jalons BI et application à livrer selon la roadmap.
