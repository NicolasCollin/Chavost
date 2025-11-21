import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Any

from src.utils.file import chemin_fichier

# --- Constante de session : toutes les bases brutes ---
RAW_DATASETS_KEY = "RAW_DATASETS"

# --- Dossier local contenant les fichiers Excel ---
# chemin_fichier() doit retourner un chemin (str ou Path) vers le dossier contenant les .xls
# On l'enveloppe toujours dans Path pour avoir .exists(), .is_dir(), etc.
DATA_FOLDER = Path(chemin_fichier())

# --- Fichiers attendus dans ce dossier ---
EXPECTED_FILES = [
    "article_precis_avec_code.xls",
    "base_commande.xls",
    "client_prospect.xls",
    "histo_clients.xls",
    "mouv_stock.xls",
]



def load_csv_safely(path_or_buf: Any)-> pd.DataFrame :
    """Charge de manière robuste un fichier Excel ou CSV."""
    name = getattr(path_or_buf, "name", "")
    path_str = str(path_or_buf)

    # Excel prioritaire
    if (
        isinstance(path_or_buf, (str, Path)) and path_str.lower().endswith((".xls", ".xlsx"))
    ) or name.lower().endswith((".xls", ".xlsx")):
        return pd.read_excel(path_or_buf)








def render_first_run_setup() -> None:
    """Charge automatiquement les bases depuis le dossier local et expose les DataFrames."""

    st.title("📂 Chargement des bases de données")

    # Vérifier existence du dossier
    if not DATA_FOLDER.exists() or not DATA_FOLDER.is_dir():
        st.error(
            f"Le dossier `{DATA_FOLDER}` est introuvable.\n\n"
            "Vérifie ce que retourne `chemin_fichier()` et la présence des fichiers Excel attendus."
        )
        # Debug éventuellement :
        st.write("Valeur de DATA_FOLDER :", repr(DATA_FOLDER))
        st.write("Type de DATA_FOLDER :", type(DATA_FOLDER))
        return

    st.info(f"Dossier détecté : `{DATA_FOLDER.resolve()}`")

    raw_dfs: dict[str, pd.DataFrame] = {}
    errors: dict[str, Exception] = {}
    missing_files: list[str] = []

    # Charger les fichiers attendus
    for fname in EXPECTED_FILES:
        fpath = DATA_FOLDER / fname
        if not fpath.exists():
            missing_files.append(fname)
            continue
        try:
            df = load_csv_safely(fpath)
            raw_dfs[fname] = df
        except Exception as e:
            errors[fname] = e

    if missing_files:
        st.warning("Fichiers manquants : " + ", ".join(missing_files))

    if errors:
        st.warning("⚠️ Certains fichiers n'ont pas pu être lus.")
        with st.expander("Détails des erreurs de lecture"):
            for name, e in errors.items():
                st.write(f"**{name}**")
                st.exception(e)

    if not raw_dfs:
        st.error("❌ Aucun fichier valide trouvé — vérifie le dossier et les noms de fichiers.")
        return

    # Stocker toutes les bases brutes dans la session
    st.session_state[RAW_DATASETS_KEY] = raw_dfs
    st.success("✅ Bases chargées et disponibles dans la session.")

    # Aperçu rapide
    st.subheader("Aperçu des bases chargées")
    for name, df in raw_dfs.items():
        with st.expander(f"{name} — {df.shape[0]} lignes × {df.shape[1]} colonnes"):
            st.dataframe(df.head())

    # Bouton d'accès aux statistiques
    st.markdown("---")
    if st.button("📊 Accès aux statistiques"):
        if hasattr(st, "switch_page"):
            try:
                st.switch_page("pages/statistiques.py")  # à adapter si besoin
            except Exception:
                st.session_state["STATS_ACCESS"] = True
                st.rerun()
        else:
            st.session_state["STATS_ACCESS"] = True
            st.rerun()


if __name__ == "__main__":
    render_first_run_setup()
