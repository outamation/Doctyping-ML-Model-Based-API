"""
Single source of truth for all environment-driven configuration.
Read once at import time. All other modules import from here.
"""
import os
from pathlib import Path

_ROOT: Path = Path(__file__).resolve().parent.parent

# ── App ────────────────────────────────────────────────────────────────
APP_MODE:       str  = os.getenv("APP_MODE", "development")
SERVER_VERIFY_KEY: str = os.getenv("SERVER_VERIFY_KEY", "")

# ── Server ─────────────────────────────────────────────────────────────
HOST: str = os.getenv("HOST", "127.0.0.1")
PORT: int = int(os.getenv("PORT", "8443"))

# ── ML model ───────────────────────────────────────────────────────────
MODEL_DIR:  Path  = _ROOT / os.getenv("MODEL_DIR", "sc_model")
MAX_LEN:    int   = int(os.getenv("MAX_LEN", "256"))
BATCH:      int   = int(os.getenv("BATCH", "32"))
LABELS:     list  = ["OTHER", "SUMMONS", "COMPLAINT"]
MIN_RAM_GB: float = float(os.getenv("MIN_RAM_GB", "2.0"))

# ── Dev output ─────────────────────────────────────────────────────────
# Only used when APP_MODE=development
DEV_OUTPUT_DIR: Path = _ROOT / "dev_output"
