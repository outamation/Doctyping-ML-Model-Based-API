import sys
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from loguru import logger
import uvicorn

from config import APP_MODE, HOST, PORT
from ml_model.loader import load_model
from routers import classify, health

if APP_MODE == "development":
    from routers import dev

# ── Logging ───────────────────────────────────────────────────────────
logger.remove()
logger.add(sys.stdout, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")


# ── Lifespan ──────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    load_model()
    yield


# ── App ───────────────────────────────────────────────────────────────
app = FastAPI(title="SC Identifier API", lifespan=lifespan)

@app.get("/")
async def root():
    return JSONResponse({"status": "API is running", "timestamp": datetime.now(timezone.utc).isoformat()})


app.include_router(health.router)
app.include_router(classify.router)

if APP_MODE == "development":
    app.include_router(dev.router)
    logger.info("DEV mode — /dev/test-pdf endpoint active")


# ── Entry point ───────────────────────────────────────────────────────
if __name__ == "__main__":
    logger.info("Starting SC Identifier API on {}:{}", HOST, PORT)
    uvicorn.run("new_main:app", host=HOST, port=PORT, reload=True)
