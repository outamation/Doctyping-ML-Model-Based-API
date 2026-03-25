"""
Process-level singleton that holds the loaded model and tokenizer.

Once populate() is called at startup the objects live for the entire
lifetime of the OS process — they are never garbage-collected because
this module keeps strong references to them.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification


@dataclass
class _ModelState:
    tokenizer: Optional[AutoTokenizer] = field(default=None, repr=False)
    model:     Optional[AutoModelForSequenceClassification] = field(default=None, repr=False)
    device:    str = "cpu"
    loaded:    bool = False

    def populate(
        self,
        tokenizer: AutoTokenizer,
        model: AutoModelForSequenceClassification,
        device: str,
    ) -> None:
        self.tokenizer = tokenizer
        self.model     = model
        self.device    = device
        self.loaded    = True

    def get(self) -> tuple[AutoTokenizer, AutoModelForSequenceClassification, str]:
        if not self.loaded:
            raise RuntimeError("Model has not been loaded yet — call load_model() at startup.")
        return self.tokenizer, self.model, self.device  # type: ignore[return-value]


# Single instance shared across the entire process
model_state = _ModelState()
