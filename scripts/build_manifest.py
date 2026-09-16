from pathlib import Path
import csv


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(".")

DATA_ROOT = Path("asr_nepali_data")

AUDIO_INDEX = Path(
    "manifests/audio_index.csv"
)

OUTPUT_FILE = Path(
    "manifests/all.csv"
)