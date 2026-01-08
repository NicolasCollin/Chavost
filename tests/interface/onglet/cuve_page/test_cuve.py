import unittest


class TestCuvePage(unittest.TestCase):
    """Smoke test : le module cuve.py doit s'importer (évite les SyntaxError/NameError)."""

    def test_import_cuve(self) -> None:
        """Import simple : si ça casse, c'est que la page ne pourra pas se charger."""
        from src.interface.onglet.cuve_page.cuve import cuve_tool  # noqa: F401


if __name__ == "__main__":
    unittest.main()
