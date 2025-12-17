"""
Tests unitaires pour les fonctions de préparation de données (prepare.py).

Ces tests vérifient le comportement des fonctions de préparation utilisées
par l'interface :
- filtrage des clients et des commandes selon une sélection donnée
- conservation des commandes lors du rattachement au stock (left join)
- complétion des séries temporelles avec des valeurs manquantes à zéro
"""

import pandas as pd

from src.interface.onglet.client_page.features.prepare import (
    build_df_full,
    prepare_client_filters,
)


class TestPrepareClientFilters:
    """Vérifications du filtrage des clients, des commandes et du rattachement au stock."""

    def test_filtre_les_clients_et_conserve_les_commandes_meme_si_stock_absent(self):
        """
        Vérifie que :
        - seuls les clients sélectionnés sont conservés
        - seules les commandes associées à ces clients sont conservées
        - les commandes sont conservées même si aucune information de stock n'existe
        """
        df = pd.DataFrame(
            {
                "nom_du_client": ["A", "B", "C"],
                "info": [1, 2, 3],
            }
        )

        df_com = pd.DataFrame(
            {
                "nom_du_client": ["A", "A", "C"],
                "n_document": [
                    100,
                    200,
                    999,
                ],  # 200 n'existe pas dans df_sto => stock manquant attendu
                "montant": [10.0, 20.0, 30.0],
            }
        )

        df_sto = pd.DataFrame(
            {
                "n_document": [100],
                "stock_info": ["S1"],
            }
        )

        df_filtre, df_com_filtre, df_stock_filtred = prepare_client_filters(
            df, df_sto, df_com, ["A", "B"]
        )

        # Clients : on garde uniquement la sélection
        assert set(df_filtre["nom_du_client"].unique()) == {"A", "B"}
        assert len(df_filtre) == 2

        # Commandes : seules celles des clients sélectionnés (ici uniquement A)
        assert set(df_com_filtre["nom_du_client"].unique()) == {"A"}
        assert len(df_com_filtre) == 2

        # Stock : left join => même nombre de lignes que les commandes filtrées
        assert len(df_stock_filtred) == len(df_com_filtre)

        # Stock manquant : la commande n_document=200 doit exister avec stock_info manquant
        row_missing = df_stock_filtred[df_stock_filtred["n_document"] == 200]
        assert len(row_missing) == 1
        assert pd.isna(row_missing.iloc[0]["stock_info"])


class TestBuildDfFull:
    """Vérifications de la complétion des données temporelles."""

    def test_complete_les_combinaisons_manquantes_et_preserve_les_valeurs(self):
        """
        Vérifie que la fonction :
        - crée toutes les combinaisons (nom, mois_annee) attendues
        - affecte une quantité nulle aux combinaisons absentes
        - conserve les quantités déjà présentes dans les données d'origine
        """
        suivi = pd.DataFrame(
            {
                "nom": ["A", "A", "B"],
                "mois_annee": ["2025-01", "2025-02", "2025-01"],
                "quantite": [5, 2, 7],
            }
        )

        df_full = build_df_full(suivi)

        # Produit cartésien attendu : noms={A,B} x mois={2025-01,2025-02} => 4 lignes
        assert len(df_full) == 4

        # Combinaison manquante (B, 2025-02) => quantite=0
        missing = df_full[
            (df_full["nom"] == "B") & (df_full["mois_annee"] == "2025-02")
        ]
        assert len(missing) == 1
        assert missing.iloc[0]["quantite"] == 0

        # Valeurs existantes préservées
        a_2025_01 = df_full[
            (df_full["nom"] == "A") & (df_full["mois_annee"] == "2025-01")
        ]
        a_2025_02 = df_full[
            (df_full["nom"] == "A") & (df_full["mois_annee"] == "2025-02")
        ]
        b_2025_01 = df_full[
            (df_full["nom"] == "B") & (df_full["mois_annee"] == "2025-01")
        ]

        assert a_2025_01.iloc[0]["quantite"] == 5
        assert a_2025_02.iloc[0]["quantite"] == 2
        assert b_2025_01.iloc[0]["quantite"] == 7
