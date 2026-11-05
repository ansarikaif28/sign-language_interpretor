"""Paths and runtime settings.

Every path here is resolved from the repository root, so the application
behaves the same no matter which directory it is launched from.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_DIR.parent

ASSETS_DIR = PACKAGE_DIR / "assets"
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUT_DIR = PROJECT_ROOT / "output"

MODEL_PATH = MODELS_DIR / "model.p"
DATASET_PATH = DATA_DIR / "data.pickle"
DEFAULT_DATA_DIR = DATA_DIR / "raw"

# Window sizes shared by the login, sign-up and dashboard screens.
WINDOW_SIZE = "1166x718"
DASHBOARD_SIZE = "856x645"

# Read .env before anything asks os.environ for a value.
load_dotenv(PROJECT_ROOT / ".env")

# 0 is usually the built-in webcam, 1 an external one.
CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", "1"))

FIREBASE_CONFIG = {
    "api_key": os.getenv("FIREBASE_API_KEY", ""),
    "auth_domain": os.getenv("FIREBASE_AUTH_DOMAIN", ""),
    "project_id": os.getenv("FIREBASE_PROJECT_ID", ""),
}


def asset(name: str) -> str:
    """Absolute path to a file in ``silent_voice/assets``."""
    return str(ASSETS_DIR / name)


def ensure_dirs() -> None:
    for directory in (DATA_DIR, MODELS_DIR, OUTPUT_DIR):
        directory.mkdir(parents=True, exist_ok=True)
