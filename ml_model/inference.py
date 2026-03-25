"""
run_inference(pages) — takes the list of PageIn objects from the request,
passes their text through the loaded model, and returns raw per-page
prediction results.

The model itself stays in ml_model.state.model_state (process-level cache).
"""
from __future__ import annotations

import numpy as np
import torch
from loguru import logger

from config import MAX_LEN, BATCH, LABELS
from ml_model.state import model_state


def _predict_batch(texts: list[str]) -> tuple[np.ndarray, list[str]]:
    tokenizer, model, device = model_state.get()

    enc = tokenizer(
        texts,
        truncation=True,
        padding=True,
        max_length=MAX_LEN,
        return_tensors="pt",
    )
    enc = {k: v.to(device) for k, v in enc.items()}

    with torch.no_grad():
        out = model(**enc)

    probs    = torch.softmax(out.logits, dim=-1).cpu().numpy()
    pred_ids = probs.argmax(axis=1)
    labels   = [LABELS[i] for i in pred_ids]
    return probs, labels


def run_inference(pages: list) -> list[dict]:
    """
    Parameters
    ----------
    pages : list of PageIn  (page_number: int, text: str)

    Returns
    -------
    list of dicts, one per page:
        {
            "page_number": int,
            "pred_label":  str,          # "OTHER" | "SUMMONS" | "COMPLAINT"
            "p_other":     float,
            "p_summons":   float,
            "p_complaint": float,
        }
    """
    texts = [p.text for p in pages]
    page_nums = [p.page_number for p in pages]

    all_probs:  list[np.ndarray] = []
    all_labels: list[str]        = []

    for i in range(0, len(texts), BATCH):
        probs, labels = _predict_batch(texts[i : i + BATCH])
        all_probs.append(probs)
        all_labels.extend(labels)

    probs_matrix = np.vstack(all_probs)

    results = []
    for idx, (page_num, label) in enumerate(zip(page_nums, all_labels)):
        results.append({
            "page_number":  page_num,
            "pred_label":   label,
            "p_other":      round(float(probs_matrix[idx, 0]), 4),
            "p_summons":    round(float(probs_matrix[idx, 1]), 4),
            "p_complaint":  round(float(probs_matrix[idx, 2]), 4),
        })

    logger.debug("Inference done — {} pages scored", len(results))
    return results
