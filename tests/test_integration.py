"""
INTEGRATION TESTS — hit the actual ChromaDB and real Groq API.

Test markers:
  @pytest.mark.slow  — tests that call Groq and take > 30 seconds
  (no marker)        — fast tests that only query ChromaDB, no Groq calls

Run only fast integration tests:   pytest tests/test_integration.py -m "not slow" -v
Run the full suite including slow:  pytest tests/test_integration.py -v
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)


# ---------------------------------------------------------------------------
# Fast tests — ChromaDB only, no Groq calls
# ---------------------------------------------------------------------------

def test_integration_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    # Health now actively probes DB and returns count info
    assert "ok" in data["database"]
    assert "groq_configured" in data

def test_integration_companies():
    response = client.get("/companies")
    assert response.status_code == 200
    data = response.json()
    tickers = [c["ticker"] for c in data]
    assert "AAPL" in tickers
    assert "MSFT" in tickers
    assert "TSLA" in tickers

def test_integration_ask_invalid():
    """No Groq call: missing ticker returns early with empty sources."""
    payload = {"ticker": "INVALID", "text": "What are the risks?"}
    response = client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "INVALID"
    assert "No filing data found" in data["answer"]
    assert len(data["sources"]) == 0

def test_integration_diff_invalid_years():
    """No Groq call: missing year data raises ValueError → 404."""
    payload = {"ticker": "AAPL", "year1": "1990", "year2": "1991"}
    response = client.post("/diff", json=payload)
    assert response.status_code == 404
    assert "Missing data" in response.json()["detail"]

def test_integration_diff_same_years():
    """No Groq call: same year raises ValueError → 404."""
    payload = {"ticker": "AAPL", "year1": "2024", "year2": "2024"}
    response = client.post("/diff", json=payload)
    assert response.status_code == 404
    assert "different" in response.json()["detail"]


# ---------------------------------------------------------------------------
# Slow tests — real Groq API calls (marked separately to control quota use)
# ---------------------------------------------------------------------------

@pytest.mark.slow
def test_integration_ask_valid():
    payload = {"ticker": "AAPL", "text": "What supply-chain risks does Apple disclose?"}
    response = client.post("/ask", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert len(data["answer"]) > 20
    assert len(data["sources"]) > 0
    for source in data["sources"]:
        assert source["ticker"] == "AAPL"

@pytest.mark.slow
def test_integration_company_isolation():
    """Each ticker must return ONLY its own chunks."""
    for ticker in ["AAPL", "MSFT"]:
        response = client.post("/ask", json={"ticker": ticker, "text": "What are the core business areas?"})
        assert response.status_code == 200
        for source in response.json()["sources"]:
            assert source["ticker"] == ticker, f"Contamination: expected {ticker}, got {source['ticker']}"

@pytest.mark.slow
def test_integration_litigation():
    payload = {"query": "What legal proceedings or litigation risks appear across these companies?"}
    response = client.post("/litigation", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["answer"]) > 20
    assert len(data["matches"]) > 0
    for match in data["matches"]:
        assert match["section"] == "Item 3"
        assert match["fiscal_year"]
        assert match["ticker"] in ["AAPL", "MSFT", "TSLA"]

@pytest.mark.slow
def test_integration_diff_valid():
    """
    Real map-reduce diff: MSFT 2024 vs 2025.
    NOTE: Run this test in isolation, not alongside other Groq tests.
    Command: pytest tests/test_integration.py::test_integration_diff_valid -v -s
    Takes ~15 minutes due to rate-limit-safe pacing.
    """
    payload = {"ticker": "MSFT", "year1": "2024", "year2": "2025"}
    response = client.post("/diff", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["ticker"] == "MSFT"
    assert data["year1"] == "2024"
    assert data["year2"] == "2025"
    assert len(data["summary"]) > 10
    assert "Failed to parse" not in data["summary"], "JSON parsing failed — check model output"
    assert isinstance(data["changes"], list)

    print("\n[DIFF TEST OUTPUT]")
    print(json.dumps(data, indent=2))
    print("[END DIFF TEST OUTPUT]\n")
