import sys
from edgar_utils import get_cik, get_recent_10ks, fetch_filing_html, extract_risk_factors, extract_legal_proceedings
from sentence_transformers import SentenceTransformer
import chromadb

def chunk_text(text, chunk_size=800, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

def embed_section(collection, model, ticker, year, section_name, text):
    if not text or len(text) < 200:
        print(f"  Skipped {section_name} for {year} — not found or too short (likely a redirect notice)")
        return
    # ... rest stays the same

    chunks = chunk_text(text)
    for i, chunk in enumerate(chunks):
        embedding = model.encode(chunk).tolist()
        collection.upsert(
            ids=[f"{ticker}_10k_{year}_{section_name.replace(' ', '_')}_{i}"],
            embeddings=[embedding],
            documents=[chunk],
            metadatas=[{
                "ticker": ticker.upper(),
                "filing_type": "10-K",
                "fiscal_year": year,
                "section": section_name
            }]
        )
    print(f"  Embedded {len(chunks)} chunks for {section_name} {year}")

def ingest(ticker):
    cik = get_cik(ticker)
    if not cik:
        print(f"Couldn't find a CIK for ticker '{ticker}'")
        return

    print(f"Found CIK {cik} for {ticker}")

    model = SentenceTransformer("all-MiniLM-L6-v2")
    db_client = chromadb.PersistentClient(path="./chroma_db")
    collection = db_client.get_or_create_collection(name="filings")

    filings = get_recent_10ks(cik, limit=2)

    for filing in filings:
        html = fetch_filing_html(cik, filing["accession"], filing["document"])
        year = filing["year"]

        risk_text = extract_risk_factors(html)
        embed_section(collection, model, ticker, year, "Item 1A", risk_text)

        legal_text = extract_legal_proceedings(html)
        embed_section(collection, model, ticker, year, "Item 3", legal_text)

if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    ingest(ticker)