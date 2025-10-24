

import pytest
from src.main import main  # Import the main function to test

# Basic smoke test to ensure the main function runs without errors
def test_main_runs_without_error():
    try:
        result = main()
    except Exception as e:
        pytest.fail(f"main() raised an exception: {e}")