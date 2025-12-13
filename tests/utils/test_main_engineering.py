"""Tests unitaires pour la fonction load_csv_safely.
Vérifie la lecture correcte de fichiers et la robustesse face à des types inconnus."""

import pandas as pd
import pytest
from pathlib import Path

from src.utils.main_engineering import load_csv_safely


class TestLoadCsvSafely:
    """Tests unitaires simples pour load_csv_safely."""

    def test_lit_un_excel_en_appelant_read_excel(self, monkeypatch, tmp_path: Path):
        """Vérifie que load_csv_safely utilise read_excel pour un fichier Excel."""
        expected = pd.DataFrame({"a": [1]})  # dataframe attendu

        def fake_read_excel(_path):
            return expected  # on évite un vrai fichier Excel

        monkeypatch.setattr(pd, "read_excel", fake_read_excel)  # mock I/O

        file_path = tmp_path / "test.xls"
        df = load_csv_safely(file_path)

        assert df is expected


class TestRobustesse:
    """Tests de robustesse basiques."""

    def test_type_inconnu_retourne_none(self):
        """Vérifie que load_csv_safely retourne None pour un type de fichier inconnu."""
        assert load_csv_safely("fichier_inconnu.zzz") is None  # comportement actuel