"""
DEV-ONLY router — registered only when APP_MODE=development.
Upload a raw PDF and get back per-page model predictions for quick testing.
"""
import time

from fastapi import APIRouter, File, HTTPException, UploadFile
from loguru import logger

from ml_model.inference import run_inference
from models.schemas import LLMOutput, PageIn
from utils.aggregation import build_llm_response
from utils.pdf import extract_pages_from_bytes

router = APIRouter(prefix="/dev", tags=["dev"])


@router.post("/test-pdf", response_model=LLMOutput)
async def test_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    start = time.perf_counter()

    pdf_bytes = await file.read()
    logger.info("DEV /test-pdf — received '{}' ({} bytes)", file.filename, len(pdf_bytes))

    pages_raw = extract_pages_from_bytes(pdf_bytes)
    if not pages_raw:
        raise HTTPException(status_code=422, detail="No readable text found in PDF.")

    pages   = [PageIn(**p) for p in pages_raw]
    results = run_inference(pages)

    response = build_llm_response(0, file.filename, results, time_taken=time.perf_counter() - start)

    doc_counts = {d["document_type"]: len(d["page_numbers"]) for d in response["documents"]}
    logger.info("DEV /test-pdf — '{}' done | {}", file.filename, doc_counts)

    return response
