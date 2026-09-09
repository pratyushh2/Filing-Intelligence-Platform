from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class AskRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10, description="Company ticker symbol (e.g., AAPL)")
    text: str = Field(..., min_length=5, max_length=1000, description="The user's question about the company")

    @field_validator('ticker')
    @classmethod
    def format_ticker(cls, v: str) -> str:
        return v.strip().upper()

class Source(BaseModel):
    ticker: str
    fiscal_year: str
    section: str
    text: str
    source_url: Optional[str] = None

class AskResponse(BaseModel):
    answer: str
    ticker: str
    sources: List[Source]

class DiffRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10, description="Company ticker symbol")
    year1: str = Field(..., min_length=4, max_length=4, description="The earlier year (e.g., '2024')")
    year2: str = Field(..., min_length=4, max_length=4, description="The later year (e.g., '2025')")

    @field_validator('ticker')
    @classmethod
    def format_ticker(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator('year1', 'year2')
    @classmethod
    def validate_year(cls, v: str) -> str:
        v = v.strip()
        if not v.isdigit():
            raise ValueError("Year must be a 4-digit number")
        return v

class DiffChange(BaseModel):
    type: str = Field(..., description="Type of change (e.g., 'added', 'removed', 'changed')")
    topic: str
    description: str

class DiffResponse(BaseModel):
    ticker: str
    year1: str
    year2: str
    summary: str
    changes: List[DiffChange]
    sources: List[Source] = []

class LitigationRequest(BaseModel):
    query: str = Field(..., min_length=5, max_length=1000, description="The user's query regarding litigation across companies")

class LitigationMatch(BaseModel):
    ticker: str
    fiscal_year: str
    section: str
    text: str

class LitigationResponse(BaseModel):
    answer: str
    matches: List[LitigationMatch]

class CompanyInfo(BaseModel):
    ticker: str
    name: str = ""
    years: List[str]

class HealthResponse(BaseModel):
    status: str
    database: str
    groq_configured: bool
