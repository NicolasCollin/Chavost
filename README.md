# Chavost — Mission de consulting data (Coopérative Chavost)

## 1) Contexte

**Chavost** est une marque de champagne née au sein de la coopérative de **Chavot‑Courcourt**. Une spécificité forte de la maison est la cuvée **sans sulfites ajoutés** (créée en 2019, commercialisée après 15 mois d’élevage). Cette approche implique un suivi œnologique plus fin (prévention de l’oxydation par gaz neutres, cuves inox hermétiques, contrôles rapprochés), et participe à un profil aromatique plus « pur ».  
Dans le même temps, la marque connaît une **croissance rapide** : des dizaines de milliers de bouteilles vendues la première année et **près de 100 000 de plus en 2024**. Cette montée en charge multiplie les **pays**, **importateurs**, **cuvées**, **formats** et **volumes stockés**, et rend critique la **structuration et l’exploitation** de la donnée commerciale.

## 2) Problématique

Les systèmes actuels ne permettent d’exploiter qu’une faible part de l’information disponible. Les questions métier sont nombreuses :  
- Comment évoluent les **ventes par pays**, par **importateur**, par **cuvée** et par **format** (75 cl, magnum, jéroboam, etc.) ?  
- Quelles **saisonnalités** (Noël, pics ponctuels) et quels **moments forts** stimuler (prévisions d’habillage, préparation des stocks) ?  
- Quels **prix moyens** et quelles **différences géographiques** observer ?  
- Comment mieux **piloter** la croissance avec des **indicateurs** clairs et un **outillage** accessible ?

## 3) Objectifs de la mission

1. **Créer la collaboration** et cadrer les besoins (entretiens, périmètre, planning).  
2. **Data Engineering** : transformer des **Excel bruts** (cellules fusionnées, totaux, mises en forme) en **base exploitable** (une ligne = une transaction).  
3. **Analytics & BI** : produire un **rapport BI** (Power BI) et une **interface** (Streamlit) pour explorer les ventes par pays/importateur/cuvée/format, suivre les tendances, et appuyer la décision.

## 4) Ce que fait le projet aujourd’hui

- **Nettoyage/structuration** des fichiers Excel hétérogènes.  
- **Construction d’une base tabulaire** avec les champs clefs (client, produit/cuvée, catégorie, format, année, quantité EQB, montant HT).  
- **Automatisation** du pipeline pour rejouer le traitement lors des mises à jour.  
- **Application** (base) pour parcourir et visualiser les données préparées.  
- Préparation des livrables **Power BI** et **Streamlit** pour la suite du projet.

---

## 5) Arborescence du dépôt

```
chavost/
├── data/
│   ├── raw/              # Fichiers sources Excel (non versionnés si volumineux)
│   └── processed/        # Données nettoyées et prêtes à l’analyse
├── src/
│   ├── main.py           # Point d’entrée de l’application (exécution locale)
│   ├── cleaning/         # Fonctions de nettoyage et normalisation
│   ├── analysis/         # Fonctions d’agrégation / stats / graphiques
│   └── utils/            # Outils divers
├── resultat.csv          # Sorties de résultats (ex. récap/indicateurs)
├── pred_test.csv         # Jeu de test (ex. prédictions / démonstration)
├── pyproject.toml        # Dépendances et configuration (uv)
└── README.md
```

> Remarque : l’arborescence peut évoluer ; reportez‑vous aux sous‑dossiers `src/cleaning`, `src/analysis` pour le détail du pipeline.

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
uv venv
uv sync
```

### 6.3 Lancer l’application locale

```bash
uv run ./src/main.py
```

> Astuce : si vous utilisez souvent cette commande, créez un alias shell, par exemple :  
> `alias chavost='uv run ./src/main.py'`

### 6.4 Données
- Placez vos fichiers Excel sources dans `data/raw/`.  
- Les sorties structurées seront générées dans `data/processed/` (selon le pipeline en place).  
- Les fichiers `resultat.csv` et `pred_test.csv` servent d’exemple pour la partie démonstration/visualisation.

### 6.5 Dépannage courant
- **uv ne trouve pas Python 3.12** : installez la version correspondante puis rejouez `uv venv && uv sync`.  
- **Erreur d’import** : vérifiez que vous exécutez depuis la racine du dépôt et utilisez `uv run ./src/main.py`.  
- **Données volumineuses** : ne versionnez pas `data/raw/` dans Git ; utilisez `.gitignore`.

---

## 7) Stack technique

- **Python** (3.13), **Pandas** pour le traitement.  
- **uv** pour les environnements et l’exécution.  
- **Streamlit / HTML / CSS** pour l’interface (prochain jalon).  
- **Power BI** pour le rapport BI (prochain jalon).  
- Gestion de version **GitLab**, CI/CD en cours de préparation selon les besoins du client.

---

## 8) Roadmap synthétique

- **S1 — Cadrage** : entretiens, identification des besoins, planning.  
- **S2 — Data Eng.** : nettoyage Excel → base tabulaire, automatisation.  
- **S3 — BI** : construction du rapport Power BI (ventes par pays/importateur/cuvée/format, saisonnalité).  
- **S4 — App** : interface Streamlit pour exploration dynamique et filtres.  
- **S5 — Itérations** : retours client, priorisation des KPIs, mise en production graduelle.

---

## 9) Équipe & encadrement

- **Nikita POMOZOV** — Data engineering & cadrage
- **Nicolas COLLIN** — Développement & automatisation
- **Matthis ARVOIS** — Analyses & visualisations

Encadrement : **Emmanuelle GAUTHERAT** (Université de Reims Champagne‑Ardenne).

---

## 10) Licence et statut

Projet académique dans le cadre du Master, destiné à un **usage interne** à la coopérative et à l’équipe pédagogique.  
**Statut** : en développement, jalons BI et application à livrer selon la roadmap.

---

## 11) Questions fréquentes

**Puis‑je lancer directement un dashboard ?**  
Aujourd’hui, l’entrée principale est `src/main.py`. Le dashboard Streamlit/BI sera livré au jalon suivant.

**Comment rejouer le pipeline de nettoyage ?**  
Placez les sources dans `data/raw/`, exécutez l’application (`uv run ./src/main.py`) et vérifiez `data/processed/`.

**Puis‑je utiliser conda/venv à la place d’uv ?**  
Oui, mais la configuration du projet est optimisée pour `uv`. Si vous changez d’outil, adaptez les commandes d’installation.
