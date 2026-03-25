"""
load_model()  — called ONCE at FastAPI startup via the lifespan hook.

After this function returns:
  • tokenizer and model objects are stored in ml_model.state.model_state
  • the OS process holds strong references → objects stay in RAM for
    the entire lifetime of the server process (process-level caching)
  • all resource diagnostics have been logged
"""
import torch
from loguru import logger
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from config import MODEL_DIR, MIN_RAM_GB
from ml_model.state import model_state
from ml_model.diagnostics import (
    log_system_info,
    log_process_info,
    log_model_memory_delta,
)


def load_model() -> None:
    if model_state.loaded:
        logger.warning("load_model() called but model is already loaded — skipping.")
        return

    logger.info("══════════  ML MODEL LOAD  ══════════")
    logger.info("Model directory : {}", MODEL_DIR)

    if not MODEL_DIR.exists():
        raise FileNotFoundError(f"Model directory not found: {MODEL_DIR}")

    # ── 1. Log machine / OS once ───────────────────────────────────────
    log_system_info()

    # ── 2. Snapshot RAM *before* load ─────────────────────────────────
    before = log_process_info(label="BEFORE LOAD")

    # ── 3. Warn if not enough free RAM ────────────────────────────────
    if before["sys_free_gb"] < MIN_RAM_GB:
        logger.warning(
            "Only {} GB free RAM available — model requires at least {} GB. "
            "Performance may degrade or loading may fail.",
            before["sys_free_gb"],
            MIN_RAM_GB,
        )

    # ── 4. Choose device ──────────────────────────────────────────────
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info("Compute device  : {}", device.upper())

    # ── 5. Load tokenizer + model ─────────────────────────────────────
    logger.info("Loading tokenizer…")
    tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR), use_fast=True)

    logger.info("Loading model weights…")
    model = AutoModelForSequenceClassification.from_pretrained(str(MODEL_DIR))
    model.to(device)
    model.eval()

    # ── 6. Pin into process-level singleton ───────────────────────────
    model_state.populate(tokenizer, model, device)
    logger.info("Model pinned in process memory (process-level cache active).")

    # ── 7. Snapshot RAM *after* load + log delta ──────────────────────
    after = log_process_info(label="AFTER LOAD")
    log_model_memory_delta(before, after)

    logger.info("══════════  MODEL READY  ══════════")
