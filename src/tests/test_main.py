import pytest
from src.main import main  # Import the main function to test


# Basic smoke test to ensure the main function runs without errors
def test_main_runs_without_error():
    try:
        main()
    except Exception as e:
        pytest.fail(f"main() raised an exception: {e}")


# ----------------------- Utils module tests -----------------------


def test_utils_main_callable():
    """
    Ensure src.utils.main exposes a callable `main`.
    This does NOT execute the Streamlit app; it only checks the function exists.
    """
    try:
        from src.utils.main import main  # type: ignore
    except Exception as e:
        pytest.fail(f"Importing src.utils.main failed: {e}")
    assert callable(main), "src.utils.main.main should be callable"


def test_aliases_structure_if_present():
    """
    If src.utils.aliases defines ALIASES, it should be a dict with string keys.
    Skip if ALIASES is not defined to keep the test suite robust.
    """
    try:
        import importlib

        aliases_mod = importlib.import_module("src.utils.aliases")
    except Exception as e:
        pytest.fail(f"Importing src.utils.aliases failed: {e}")

    if not hasattr(aliases_mod, "ALIASES"):
        pytest.skip("ALIASES not defined in src.utils.aliases")

    ALIASES = getattr(aliases_mod, "ALIASES")
    assert isinstance(ALIASES, dict), "ALIASES should be a dict"
    for k in ALIASES.keys():
        assert isinstance(k, str), "ALIASES keys should be strings"


def test_utils_package_init_importable_and_all_if_present():
    """
    Ensure src.utils package imports.
    If __all__ exists, verify it's a sequence of strings.
    """
    try:
        import src.utils as utils_pkg  # type: ignore
    except Exception as e:
        pytest.fail(f"Importing src.utils package failed: {e}")

    if hasattr(utils_pkg, "__all__"):
        all_symbols = getattr(utils_pkg, "__all__")
        assert isinstance(
            all_symbols, (list, tuple)
        ), "__all__ should be a list or tuple"
        for sym in all_symbols:
            assert isinstance(sym, str), "Entries in __all__ should be strings"
