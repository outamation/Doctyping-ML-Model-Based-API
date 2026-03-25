from pathlib import Path

from fastapi import APIRouter, Header, HTTPException
from loguru import logger

from config import APP_MODE, SERVER_VERIFY_KEY
from ml_model.inference import run_inference
from models.schemas import ClassifyRequest, ClassifyResponse
from utils import dev_output
from utils.aggregation import build_response

router = APIRouter(tags=["classify"])


@router.post("/classify", response_model=ClassifyResponse)
def classify(
    request: ClassifyRequest,
    x_verify_key: str = Header(...),
):
    if x_verify_key != SERVER_VERIFY_KEY:
        logger.warning(
            "Unauthorized request — invalid verify key for file_id={}", request.file_id
        )
        raise HTTPException(status_code=401, detail="Invalid verify key")

    logger.info(
        "Classify request | file_id={} | pages={} | env={} | client={}",
        request.file_id,
        request.total_pages,
        request.environment,
        request.client_meta_data.loan_client,
    )

    results = run_inference(request.pages)

    pdf_name = Path(request.raw_pdf_path).name
    response = build_response(request.file_id, pdf_name, request.total_pages, results)

    if APP_MODE == "development":
        dev_output.save(request.file_id, request.model_dump(), response)

    logger.info(
        "Classify done | file_id={} | summons={} | complaint={}",
        request.file_id,
        response["pred_summons_count"],
        response["pred_complaint_count"],
    )

    return response
