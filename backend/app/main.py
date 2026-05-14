from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import ENV_FILE, is_openai_configured, settings
from app.database import create_db_and_tables
from app.routers import documents, exports, uploads

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    create_db_and_tables()
    logger.info("Settings loaded from %s", ENV_FILE)
    if is_openai_configured():
        logger.info("OPENAI_API_KEY is configured.")
    else:
        logger.warning(
            "OPENAI_API_KEY is missing or still set to the placeholder. "
            "Edit backend/.env and restart the backend."
        )
    yield


app = FastAPI(
    title="Bilagspilot API",
    description="Human-in-the-loop bilagsassistent for porteføljedemo.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(uploads.router)
app.include_router(documents.router)
app.include_router(exports.router)


@app.get("/api/health")
def health_check() -> dict[str, str | bool]:
    return {
        "status": "ok",
        "openai_configured": is_openai_configured(),
    }
