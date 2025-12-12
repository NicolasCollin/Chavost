import json
import os
import platform
from dataclasses import dataclass
from pathlib import Path
from typing import Final, Mapping, Sequence

import pandas as pd

from src.utils.main_engineering import load_csv_safely


CHEMIN_FICHIER_JSON: Final[Path] = Path("secrets/chemins.json")  # JSON cache for discovered paths
RAW_DATASETS_KEY: Final[str] = "RAW_DATASETS"  # legacy key kept for compatibility
EXPECTED_FILES: Final[list[str]] = [
    "article_precis_avec_code.xls",
    "base_commande.xls",
    "client_prospect.xls",
    "histo_clients.xls",
    "mouv_stock.xls",
]


@dataclass(frozen=True)
class FolderLocator:
    """Locate and validate a target folder, with a JSON cache for faster lookup."""

    cache_file: Path = CHEMIN_FICHIER_JSON  # where cached base paths are stored

    def load_cached_paths(self) -> list[str]:
        """Return cached base paths from the JSON cache file."""

        if not self.cache_file.exists():
            return []

        try:
            with self.cache_file.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except json.JSONDecodeError:
            return []

        return [str(x) for x in data] if isinstance(data, list) else []

    def save_cached_paths(self, paths: list[str]) -> None:
        """Persist base paths to the JSON cache file."""

        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        with self.cache_file.open("w", encoding="utf-8") as handle:
            json.dump(paths, handle, indent=4)

    @staticmethod
    def is_valid_folder(folder_path: str, expected_files: Sequence[str] | None = None) -> bool:
        """Return True if the folder exists and contains all expected files (if provided)."""

        folder = Path(folder_path)

        try:
            if not folder.is_dir():
                return False
        except OSError:
            return False

        if not expected_files:
            return True

        try:
            present = {entry.name for entry in os.scandir(folder)}
        except OSError:
            return False

        return set(expected_files).issubset(present)

    @staticmethod
    def find_folder_by_name(folder_name: str) -> str | None:
        """Search recursively for a folder by name (Windows/macOS/Linux)."""

        system = platform.system()

        if system == "Windows":
            start_paths = ["C:/Users/"]  # keep it conservative to avoid very long scans
        else:
            start_paths = [str(Path.home())]

        for start_path in start_paths:
            if not os.path.exists(start_path):
                continue

            for root, dirs, _files in os.walk(start_path):
                if folder_name in dirs:
                    return os.path.join(root, folder_name)

        return None

    def resolve_folder(self, folder_name: str, expected_files: Sequence[str] | None = None) -> str | None:
        """Resolve a folder path using cache first, then a slow recursive search."""

        cached_paths = self.load_cached_paths()

        for base in cached_paths:
            base_path = Path(base)

            if self.is_valid_folder(str(base_path), expected_files):
                return str(base_path)

            candidate = base_path / folder_name
            if self.is_valid_folder(str(candidate), expected_files):
                return str(candidate)

        found = self.find_folder_by_name(folder_name)
        if found and self.is_valid_folder(found, expected_files):
            if found not in cached_paths:
                cached_paths.append(found)
                self.save_cached_paths(cached_paths)
            return found

        return None


@dataclass(frozen=True)
class DatasetLoader:
    """Load expected datasets from a resolved folder."""

    data_folder: Path
    expected_files: Sequence[str] = tuple(EXPECTED_FILES)

    def load_all(self) -> dict[str, pd.DataFrame]:
        """Load all expected files into memory and return a dict keyed by filename."""

        data: dict[str, pd.DataFrame] = {}

        for filename in self.expected_files:
            file_path = self.data_folder / filename
            data[filename] = load_csv_safely(file_path)

        return data

    def load_one(self, filename: str) -> pd.DataFrame:
        """Load a single expected file by filename."""

        if filename not in set(self.expected_files):
            raise ValueError(f"Unexpected filename: {filename}")

        return load_csv_safely(self.data_folder / filename)


_locator = FolderLocator()
_data_folder_str = _locator.resolve_folder("test_export", EXPECTED_FILES)
if _data_folder_str is None:
    raise FileNotFoundError(
        "Unable to find the 'test_export' folder containing the expected files. "
        "Check the file location or update secrets/chemins.json."
    )

DATA_FOLDER: Final[Path] = Path(_data_folder_str)  # resolved folder containing the exported files
_loader = DatasetLoader(DATA_FOLDER)


def take_all_file() -> Mapping[str, pd.DataFrame]:
    """Backward-compatible helper: load every dataset and return a mapping."""

    return _loader.load_all()


def df_commande_file() -> pd.DataFrame:
    return _loader.load_one("base_commande.xls")


def df_article_file() -> pd.DataFrame:
    return _loader.load_one("article_precis_avec_code.xls")


def df_client_prosp_file() -> pd.DataFrame:
    return _loader.load_one("client_prospect.xls")


def df_clients_file() -> pd.DataFrame:
    return _loader.load_one("histo_clients.xls")


def df_stok_file() -> pd.DataFrame:
    return _loader.load_one("mouv_stock.xls")
