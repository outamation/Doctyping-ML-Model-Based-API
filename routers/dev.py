"""
DEV-ONLY router — registered only when APP_MODE=development.
Upload a raw PDF and get back per-page model predictions for quick testing.
"""
from fastapi import APIRouter, File, HTTPException, UploadFile
from loguru import logger

from ml_model.inference import run_inference
from models.schemas import PageIn
from utils.aggregation import build_response
from utils.pdf import extract_pages_from_bytes

router = APIRouter(prefix="/dev", tags=["dev"])


@router.post("/test-pdf")
async def test_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    pdf_bytes = await file.read()
    logger.info("DEV /test-pdf — received '{}' ({} bytes)", file.filename, len(pdf_bytes))

    pages_raw = extract_pages_from_bytes(pdf_bytes)
    if not pages_raw:
        raise HTTPException(status_code=422, detail="No readable text found in PDF.")

    pages   = [PageIn(**p) for p in pages_raw]
    results = run_inference(pages)

    logger.info(
        "DEV /test-pdf — '{}' done ({} pages scored)", file.filename, len(results)
    )

    pdf_name = file.filename
    total_pages = len(pages)
    response = build_response(0, pdf_name, total_pages, results)

    logger.info(
        "DEV /test-pdf — '{}' done | summons={} | complaint={}",
        pdf_name,
        response["pred_summons_count"],
        response["pred_complaint_count"],
    )

    return response
