from fastapi import APIRouter
from loguru import logger

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    logger.info("Health check called")
    return {"status": "ok"}
