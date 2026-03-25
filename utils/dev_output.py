"""
Saves request payload + raw model output to disk.
Only called when APP_MODE=development.
"""
import json
from datetime import datetime

from loguru import logger

from config import DEV_OUTPUT_DIR


def save(file_id: int, request_dump: dict, model_output: list[dict]) -> None:
    DEV_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = DEV_OUTPUT_DIR / f"{file_id}_{ts}.json"

    payload = {
        "request":      request_dump,
        "model_output": model_output,
    }

    out_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    logger.info("DEV — saved output to {}", out_path)
