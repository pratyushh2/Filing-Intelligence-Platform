from fastapi import APIRouter
from app.models import HealthResponse
from app.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Verifies the API is running, ChromaDB is accessible, and the filings collection exists."
)
def health_endpoint():
    db_status = "error"
    try:
        from app.services.db import get_collection
        col = get_collection()
        # Confirm it's accessible with a count (fast, no embeddings needed)
        count = col.count()
        db_status = f"ok ({count} chunks in filings collection)"
    except Exception as e:
        logger.error(f"Health check DB probe failed: {e}")

    return HealthResponse(
        status="ok",
        database=db_status,
        groq_configured=bool(settings.GROQ_API_KEY)
    )
