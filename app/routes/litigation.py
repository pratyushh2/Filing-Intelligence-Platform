from fastapi import APIRouter, HTTPException
from app.models import LitigationRequest, LitigationResponse
from app.services.litigation import scan_litigation
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/litigation", response_model=LitigationResponse, summary="Scan litigation and legal proceedings", description="Searches Legal Proceedings (Item 3) across all supported companies to answer litigation-related queries.")
def litigation_endpoint(request: LitigationRequest):
    try:
        return scan_litigation(request)
    except Exception as e:
        logger.error(f"Error in /litigation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while processing litigation scan.")
