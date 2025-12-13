"""
Tests unitaires pour les fonctions utilitaires liées aux chemins et au chargement de fichiers.

Objectifs :
- vérifier la validation des dossiers (présence des fichiers attendus)
- garantir un comportement reproductible pour la recherche de dossiers
- documenter le comportement actuel de load_csv_safely (Excel OK, CSV non géré)

Ces tests sont volontairement simples et isolés du système de fichiers réel
afin d'être stables en CI.
"""

import pandas as pd
from pathlib import Path

from src.utils.load_files import dossier_valide, chemin_fichier
from src.utils.main_engineering import load_csv_safely


class TestDossierValide:
    """Tests unitaires pour la fonction dossier_valide."""

    def test_dossier_existant_sans_contrainte(self, tmp_path: Path):
        """Un dossier existant sans contrainte de fichiers doit être valide."""
        assert dossier_valide(str(tmp_path), None)

    def test_dossier_valide_avec_fichiers_attendus(self, tmp_path: Path):
        """Le dossier est valide si tous les fichiers attendus sont présents."""
        (tmp_path / "a.txt").touch()
        (tmp_path / "b.txt").touch()

        assert dossier_valide(str(tmp_path), ["a.txt", "b.txt"])

    def test_dossier_invalide_si_fichier_manquant(self, tmp_path: Path):
        """Le dossier est invalide si un fichier attendu est manquant."""
        (tmp_path / "a.txt").touch()

        assert not dossier_valide(str(tmp_path), ["a.txt", "b.txt"])


class TestCheminFichier:
    """Tests unitaires pour la fonction chemin_fichier."""

    def test_chemin_fichier_retourne_none_si_introuvable(self, monkeypatch):
        """Si aucun dossier n'est trouvé, la fonction doit retourner None."""
        # On neutralise le cache JSON pour ne pas dépendre de ta machine  # test reproductible
        monkeypatch.setattr("src.utils.load_files.charger_chemins", lambda: [])

        # On force la recherche lente à ne rien trouver  # évite un scan disque
        monkeypatch.setattr("src.utils.load_files.find_folder", lambda _name: None)

        assert chemin_fichier("dossier_inexistant") is None


class TestLoadCsvSafely:
    """Tests unitaires simples pour load_csv_safely (comportement actuel)."""

    def test_load_excel_via_mock(self, monkeypatch, tmp_path: Path):
        """Un fichier Excel (.xls) est chargé via pandas.read_excel."""
        expected = pd.DataFrame({"a": [1], "b": [2]})

        def fake_read_excel(_path):
            return expected  # évite un vrai fichier Excel

        monkeypatch.setattr(pd, "read_excel", fake_read_excel)

        file = tmp_path / "test.xls"
        df = load_csv_safely(file)

        assert df is expected

    def test_csv_retourne_none_pour_l_instant(self, tmp_path: Path):
        """Les fichiers CSV ne sont pas encore pris en charge (retour None)."""
        # Comportement actuel : CSV non géré dans load_csv_safely  # reflète le code
        file = tmp_path / "test.csv"
        file.write_text("a,b\n1,2")

        assert load_csv_safely(file) is None

    def test_type_inconnu_retourne_none(self):
        """Une extension inconnue ne provoque pas d'erreur et retourne None."""
        # Comportement actuel : pas d'exception, retour None  # stable
        assert load_csv_safely("fichier_inconnu.zzz") is None
