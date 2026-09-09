from fastapi import APIRouter, HTTPException
from app.models import AskRequest, AskResponse
from app.services.rag import ask_question
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/ask", response_model=AskResponse, summary="Ask a question about a company", description="Answers a user question based on the ingested SEC filings for the given company ticker.")
def ask_endpoint(request: AskRequest):
    try:
        return ask_question(request)
    except Exception as e:
        logger.error(f"Error in /ask: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while processing the request.")
