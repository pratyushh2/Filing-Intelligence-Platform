"""
UNIT TESTS — use FastAPI TestClient. Groq calls that would be expensive are mocked.
For real end-to-end LLM integration tests, see tests/test_integration.py.
"""
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    # database field should mention "ok" and real chunk count
    assert "ok" in data["database"]
    assert "groq_configured" in data


# ---------------------------------------------------------------------------
# /companies
# ---------------------------------------------------------------------------

def test_companies():
    response = client.get("/companies")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    tickers = [c["ticker"] for c in data]
    assert "AAPL" in tickers
    assert "MSFT" in tickers
    assert "TSLA" in tickers

    aapl = next(c for c in data if c["ticker"] == "AAPL")
    assert len(aapl["years"]) > 0
    assert aapl["name"] == "Apple Inc."


# ---------------------------------------------------------------------------
# /ask — mocked Groq so no API quota consumed
# ---------------------------------------------------------------------------

def test_ask_valid_mocked():
    with patch("app.services.rag.get_groq_completion", return_value="Apple faces supply chain risks from single-source suppliers."):
        payload = {"ticker": "AAPL", "text": "What supply-chain risks does Apple disclose?"}
        response = client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert len(data["answer"]) > 10
    assert len(data["sources"]) > 0
    for source in data["sources"]:
        assert source["ticker"] == "AAPL"


def test_ask_invalid_ticker():
    """No Groq call should happen when no data is found."""
    payload = {"ticker": "INVALID", "text": "What are the risks?"}
    response = client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "No filing data found" in data["answer"]
    assert data["ticker"] == "INVALID"
    assert len(data["sources"]) == 0


def test_ask_empty_text_rejected():
    payload = {"ticker": "AAPL", "text": "Hi"}  # under min_length=5
    response = client.post("/ask", json=payload)
    assert response.status_code == 422


def test_ask_ticker_normalized():
    """Lowercase ticker should be auto-uppercased."""
    with patch("app.services.rag.get_groq_completion", return_value="Mock answer."):
        payload = {"ticker": "  aapl  ", "text": "What are the supply chain risks?"}
        response = client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"


# ---------------------------------------------------------------------------
# /diff — mocked Groq
# ---------------------------------------------------------------------------

def test_diff_valid_mocked():
    from app.models import DiffResponse
    mock_response = DiffResponse(
        ticker="MSFT", year1="2024", year2="2025",
        summary="AI regulation emerged as a new risk in 2025.",
        changes=[{"type": "added", "topic": "AI Risk", "description": "New AI regulation risk."}],
        sources=[]
    )
    # Patch the service function as called by the route
    with patch("app.routes.diff.diff_years", return_value=mock_response):
        payload = {"ticker": "MSFT", "year1": "2024", "year2": "2025"}
        response = client.post("/diff", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "MSFT"
    assert data["year1"] == "2024"
    assert data["year2"] == "2025"
    assert data["summary"] == "AI regulation emerged as a new risk in 2025."
    assert len(data["changes"]) == 1
    assert data["changes"][0]["topic"] == "AI Risk"


def test_diff_same_years():
    payload = {"ticker": "MSFT", "year1": "2024", "year2": "2024"}
    response = client.post("/diff", json=payload)
    assert response.status_code == 404
    assert "different" in response.json()["detail"]


def test_diff_missing_years():
    # No mock needed — 1990/1991 has no ChromaDB data, summarize_full_year returns ""
    # which triggers the ValueError immediately, no Groq call occurs
    payload = {"ticker": "MSFT", "year1": "1990", "year2": "1991"}
    response = client.post("/diff", json=payload)
    assert response.status_code == 404
    assert "Missing data" in response.json()["detail"]


def test_diff_invalid_year_format():
    payload = {"ticker": "MSFT", "year1": "abcd", "year2": "2025"}
    response = client.post("/diff", json=payload)
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# /litigation — mocked Groq
# ---------------------------------------------------------------------------

def test_litigation_mocked():
    with patch("app.services.litigation.get_groq_completion", return_value="Apple is involved in various legal proceedings."):
        payload = {"query": "What legal proceedings or litigation risks appear across these companies?"}
        response = client.post("/litigation", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "matches" in data


def test_litigation_empty_query_rejected():
    payload = {"query": "Hi"}  # under min_length=5
    response = client.post("/litigation", json=payload)
    assert response.status_code == 422
