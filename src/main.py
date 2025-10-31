"""Script to launch the Streamlit app."""

import subprocess
import sys
from pathlib import Path


def main():
    """Launch the Streamlit interface."""
    app_path = Path(__file__).parent / "interface" / "app.py"
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(app_path)], check=True
    )


if __name__ == "__main__":
    main()
