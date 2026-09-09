from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

# Import routers
from app.routes.ask import router as ask_router
from app.routes.diff import router as diff_router
from app.routes.litigation import router as litigation_router
from app.routes.companies import router as companies_router
from app.routes.health import router as health_router

app = FastAPI(
    title="Filing Intelligence API",
    description="API for querying and comparing SEC EDGAR 10-K filings using RAG.",
    version="1.0.0"
)

# CORS configuration
origins = [
    settings.FRONTEND_URL,
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://127.0.0.1:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router, tags=["Health"])
app.include_router(companies_router, tags=["Companies"])
app.include_router(ask_router, tags=["Q&A"])
app.include_router(diff_router, tags=["Diff"])
app.include_router(litigation_router, tags=["Litigation"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
