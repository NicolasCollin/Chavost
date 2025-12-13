"""
Tests unitaires pour les fonctions de recherche et de mise en cache des chemins.

Objectifs :
- vérifier le comportement de la recherche de dossiers (chemin_fichier)
- garantir un comportement prévisible lorsque rien n'est trouvé
- tester la lecture et l'écriture du fichier JSON de cache des chemins

Ces tests sont isolés du système réel grâce à monkeypatch afin d'assurer
leur stabilité et leur reproductibilité en CI.
"""

from pathlib import Path

from src.utils.find_path import (
    chemin_fichier,
    charger_chemins,
    enregistrer_chemins,
)


class TestCheminFichier:
    """Tests simples pour chemin_fichier."""

    def test_retourne_none_si_dossier_introuvable(self, monkeypatch):
        """Si aucun dossier n'est trouvé, la fonction doit retourner None."""
        monkeypatch.setattr(
            "src.utils.find_path.find_folder",
            lambda _: None,
        )

        assert chemin_fichier() is None

    def test_retourne_chemin_si_trouve(self, monkeypatch):
        """Si un dossier est trouvé, son chemin doit être retourné."""
        fake_path = "/home/user/test_export"

        monkeypatch.setattr(
            "src.utils.find_path.find_folder",
            lambda _: fake_path,
        )

        assert chemin_fichier() == fake_path


class TestCheminsJson:
    """Tests simples pour le fichier chemins.json."""

    def test_charger_chemins_fichier_inexistant(self, monkeypatch):
        """Si le fichier de cache n'existe pas, une liste vide est retournée."""
        monkeypatch.setattr(
            "src.utils.find_path.chemin_fichier_json",
            "fichier_inexistant.json",
        )

        assert charger_chemins() == []

    def test_enregistrer_et_charger_chemins(self, tmp_path: Path, monkeypatch):
        """Les chemins enregistrés dans le JSON doivent être relus correctement."""
        fake_json = tmp_path / "chemins.json"

        monkeypatch.setattr(
            "src.utils.find_path.chemin_fichier_json",
            str(fake_json),
        )

        chemins = ["path1", "path2"]

        enregistrer_chemins(chemins)
        loaded = charger_chemins()

        assert loaded == chemins