# Chavost — Mission de consulting data (Coopérative Chavost)

## 1) Contexte

**Chavost** est une marque de champagne née au sein de la coopérative de **Chavot‑Courcourt**. Une spécificité forte de la maison est la cuvée **sans sulfites ajoutés** (créée en 2019, commercialisée après 15 mois d’élevage). Cette approche implique un suivi œnologique plus fin (prévention de l’oxydation par gaz neutres, cuves inox hermétiques, contrôles rapprochés) et participe à un profil aromatique plus « pur ».

La marque connaît une **croissance rapide** : des dizaines de milliers de bouteilles vendues la première année et **près de 100 000 supplémentaires en 2024**. Cette montée en charge multiplie les **pays**, **importateurs**, **cuvées**, **formats** et **volumes**, rendant critique la **structuration et l’exploitation** de la donnée commerciale.

---

## 2) Problématique

Les systèmes actuels ne permettent d’exploiter qu’une partie limitée de l’information disponible. Les enjeux métier sont notamment :

- Suivre l’évolution des **ventes par pays, importateur, cuvée et format**.
- Identifier les **saisonnalités** (pics de fin d’année, opérations ponctuelles).
- Analyser les **prix moyens** et les **différences géographiques**.
- Disposer d’indicateurs fiables pour **piloter la croissance** et anticiper les besoins (stocks, habillage, logistique).

---

## 3) Objectifs de la mission

1. **Cadrage et compréhension métier** (entretiens, périmètre, planning).
2. **Data Engineering** : transformation de fichiers **Excel hétérogènes** (cellules fusionnées, totaux, mises en forme) en une **base tabulaire exploitable** (1 ligne = 1 transaction).
3. **Analytics & BI** : mise à disposition d’outils d’analyse via **Power BI** et une **application Streamlit** pour l’exploration interactive des ventes.

---

## 4) État actuel du projet

- Nettoyage et structuration de fichiers Excel bruts.
- Construction d’une **base de données tabulaire** (client, produit/cuvée, format, année, quantités EQB, montants HT).
- **Automatisation du pipeline** de transformation.
- **Application Streamlit** fonctionnelle (KPIs, filtres, tendances).
- Mise en place d’une **CI GitLab**, de **tests unitaires** et d’outils de qualité (mypy, ruff).

---

## 5) Arborescence du dépôt

```
chavost/
├── image/
│   └── logo.ico                 # Icône utilisée pour le raccourci Windows
├── secrets/
│   └── chemins.json             # Fichier de configuration des chemins (local)
├── src/
│   ├── main.py                  # Point d’entrée principal de l’application
│   ├── interface/               # Interface Streamlit
│   │   ├── app.py
│   │   ├── app_2.py
│   │   ├── onglet/
│   │   │   ├── home.py
│   │   │   └── client.py
│   │   └── tools/
│   │       └── filter.py
│   ├── utils/                   # Fonctions métier / data engineering
│   │   ├── aliases.py
│   │   ├── engineering.py
│   │   ├── find_path.py
│   │   ├── load_files.py
│   │   ├── main_engineering.py
│   │   └── fichier_R_2_engineer.R
│   └── __init__.py
├── tests/                       # Tests unitaires (miroir de src)
│   ├── utils/
│   │   ├── test_find_path.py
│   │   ├── test_load_files.py
│   │   └── test_main_engineering.py
│   └── interface/
│       └── tools/
│           └── test_filter.py
├── .gitlab-ci.yml               # Pipeline CI/CD GitLab
├── .pre-commit-config.yaml      # Hooks de qualité de code
├── .python-version              # Version Python utilisée
├── pyproject.toml               # Dépendances et configuration (uv)
├── uv.lock                      # Verrouillage des dépendances
├── CHAVOST.bat                  # Script d’installation automatique (Windows)
└── README.md                    # Documentation du projet
```

---

## 6) Installation et exécution

### 6.1 Installation automatique (Windows – recommandé)

Un script **CHAVOST.bat** est fourni pour :
- installer Git, Python et uv si nécessaire,
- cloner ou mettre à jour le dépôt (repo GitLab privé via jeton),
- créer un lanceur local et un raccourci Bureau.

Il suffit de :
1. Renseigner le **jeton GitLab** dans `CHAVOST.bat`.
2. Lancer le script et suivre les instructions.

### 6.2 Installation manuelle (développeurs)

```bash
git clone https://gitlab-mi.univ-reims.fr/coll0155/chavost.git
cd chavost
uv sync
```

### 6.3 Lancer l’application

```bash
uv run src/main.py
```

---

## 7) Tests et qualité du code

- Tests unitaires avec **pytest** (structure miroir de `src/`).
- Vérifications statiques avec **mypy**.
- Linting et formatage avec **ruff**.
- Exécution automatique via la **CI GitLab**.

---

## 8) Stack technique

- **Python 3.13**
- **pandas** pour le traitement de données
- **uv** pour la gestion d’environnement et l’exécution
- **Streamlit** pour l’interface utilisateur
- **Power BI** pour les livrables BI
- **GitLab CI/CD** pour l’intégration continue

---

## 9) Équipe & encadrement

- **Nikita Pomozov** — Analyses & visualisations
- **Nicolas Collin** — Développement & automatisation
- **Matthis Arvois** — Data engineering & cadrage

Encadrement : **Emmanuelle Gautherat** (Université de Reims Champagne‑Ardenne).

---

## 10) Statut

Projet académique de Master, destiné à un **usage interne** à la coopérative et à l’équipe pédagogique.

**Statut** : application fonctionnelle, itérations et améliorations en cours.
