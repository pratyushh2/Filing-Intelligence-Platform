from fastapi import APIRouter, HTTPException
from app.models import DiffRequest, DiffResponse
from app.services.diff import diff_years
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/diff", response_model=DiffResponse, summary="Compare risk factors across years", description="Generates a structured comparison of a company's Risk Factors (Item 1A) between two different fiscal years.")
def diff_endpoint(request: DiffRequest):
    try:
        return diff_years(request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error in /diff: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while processing the diff.")
