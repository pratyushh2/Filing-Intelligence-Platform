from fastapi import APIRouter
from app.models import CompanyInfo
from app.services.company_service import get_companies
from typing import List

router = APIRouter()

@router.get("/companies", response_model=List[CompanyInfo])
def companies_endpoint():
    return get_companies()
