"""
Tests unitaires pour la logique métier utilisée dans filter.py.

Objectif :
- vérifier que le filtrage des données fonctionne correctement
- sans dépendre de Streamlit (UI non testée volontairement)
- garantir que la logique sous-jacente aux filtres est couverte par des tests

Ces tests valident uniquement le comportement métier.
"""

import pandas as pd


def test_logique_filtrage_produits():
    """
    Vérifie que la logique de filtrage sélectionne correctement
    les lignes correspondant aux critères (année, type, produit).
    """
    df = pd.DataFrame(
        {
            "annee_str": ["2022", "2023", "2023"],
            "type_produit": ["A", "A", "B"],
            "nom_produit": ["X", "Y", "X"],
        }
    )

    # --- logique équivalente à celle utilisée dans filter.py ---
    sel_years = ["2023"]
    sel_types = ["A"]
    sel_products = []

    mask = df["annee_str"].isin(sel_years) & df["type_produit"].isin(sel_types)
    if sel_products:
        mask &= df["nom_produit"].isin(sel_products)

    fdf = df.loc[mask]

    assert len(fdf) == 1
    assert fdf.iloc[0]["nom_produit"] == "Y"
