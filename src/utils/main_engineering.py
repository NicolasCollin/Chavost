from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

import pandas as pd
import streamlit as st

from src.utils.find_path import chemin_fichier


RAW_DATASETS_KEY: Final[str] = "RAW_DATASETS"  # session key for raw datasets
SHOW_CHECK_DATA_KEY: Final[str] = "SHOW_CHECK_DATA"  # session key for UI toggle

EXPECTED_FILES: Final[list[str]] = [
    "article_precis_avec_code.xls",
    "base_commande.xls",
    "client_prospect.xls",
    "histo_clients.xls",
    "mouv_stock.xls",
]


def _resolve_data_folder() -> Path:
    """Resolve the local folder that contains the exported datasets."""

    folder = chemin_fichier()  # may be str | Path | None depending on implementation
    if folder is None:
        raise FileNotFoundError("chemin_fichier() returned None; cannot resolve data folder")

    return Path(folder)


DATA_FOLDER: Final[Path] = _resolve_data_folder()  # resolved local folder containing the Excel files


def load_file_safely(path_or_buf: Any) -> pd.DataFrame:
    """Load an Excel or CSV file with a small amount of format inference."""

    name = getattr(path_or_buf, "name", "")
    path_str = str(path_or_buf)

    is_excel = (
        isinstance(path_or_buf, (str, Path))
        and path_str.lower().endswith((".xls", ".xlsx"))
    ) or name.lower().endswith((".xls", ".xlsx"))

    if is_excel:
        return pd.read_excel(path_or_buf)

    is_csv = (
        isinstance(path_or_buf, (str, Path))
        and path_str.lower().endswith(".csv")
    ) or name.lower().endswith(".csv")

    if is_csv:
        return pd.read_csv(path_or_buf)

    raise ValueError(f"Unsupported file type for: {path_or_buf!r}")


def load_csv_safely(path_or_buf: Any) -> pd.DataFrame:
    """Backward-compatible alias for older modules."""

    return load_file_safely(path_or_buf)


@dataclass(frozen=True)
class DataChecker:
    """Streamlit helper to load and preview local datasets on demand."""

    data_folder: Path = DATA_FOLDER
    expected_files: list[str] | None = None

    def __post_init__(self) -> None:
        if self.expected_files is None:
            object.__setattr__(self, "expected_files", list(EXPECTED_FILES))

    def run(self) -> None:
        """Render the Streamlit UI and (optionally) load datasets into the session."""

        if SHOW_CHECK_DATA_KEY not in st.session_state:
            st.session_state[SHOW_CHECK_DATA_KEY] = False  # default: hidden

        show_content = bool(st.session_state[SHOW_CHECK_DATA_KEY])
        raw_dfs: dict[str, pd.DataFrame] = {}

        if show_content:
            st.title("📂 Dataset loader")

            if not self.data_folder.exists() or not self.data_folder.is_dir():
                st.error(
                    f"Folder `{self.data_folder}` was not found.\n\n"
                    "Check what `chemin_fichier()` returns and confirm the expected Excel files exist."
                )
                st.write("DATA_FOLDER value:", repr(self.data_folder))
                st.write("DATA_FOLDER type:", type(self.data_folder))
            else:
                st.info(f"Detected folder: `{self.data_folder.resolve()}`")

                errors: dict[str, Exception] = {}
                missing_files: list[str] = []

                for filename in (self.expected_files or []):
                    file_path = self.data_folder / filename

                    if not file_path.exists():
                        missing_files.append(filename)
                        continue

                    try:
                        raw_dfs[filename] = load_file_safely(file_path)
                    except Exception as exc:
                        errors[filename] = exc

                if missing_files:
                    st.warning("Missing files: " + ", ".join(missing_files))

                if errors:
                    st.warning("⚠️ Some files could not be read.")
                    with st.expander("Read errors"):
                        for file_name, err in errors.items():
                            st.write(f"**{file_name}**")
                            st.exception(err)

                if not raw_dfs:
                    st.error("❌ No valid file found — check the folder and filenames.")
                else:
                    st.session_state[RAW_DATASETS_KEY] = raw_dfs
                    st.success("✅ Datasets loaded and stored in session.")

                    st.subheader("Quick preview")
                    for file_name, df in raw_dfs.items():
                        with st.expander(f"{file_name} — {df.shape[0]} rows × {df.shape[1]} columns"):
                            st.dataframe(df.head())

        st.markdown("---")

        label = "🔽 Hide datasets" if show_content else "📂 Show loaded datasets"
        if st.button(label, key="CHECK_DATA_TOGGLE"):
            st.session_state[SHOW_CHECK_DATA_KEY] = not show_content
            st.rerun()


def check_data() -> None:
    """Backward-compatible entrypoint (kept for existing imports)."""

    DataChecker().run()


if __name__ == "__main__":
    check_data()
