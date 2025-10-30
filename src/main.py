import subprocess  # to run a CLI command
import sys  # to get current Python executable
from pathlib import Path  # to build a file path


def main():
    # chemin vers ton app Streamlit
    app_path = Path(__file__).parent / "interface" / "app.py"
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", str(app_path)], check=True
    )


if __name__ == "__main__":
    main()
