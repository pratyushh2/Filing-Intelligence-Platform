
=======
# SEC EDGAR Filing Intelligence Platform

This project is an AI-powered SEC EDGAR 10-K Filing Intelligence Platform. It extracts important sections from 10-K filings (Risk Factors and Legal Proceedings), stores them using local embeddings in ChromaDB, and uses a Retrieval-Augmented Generation (RAG) architecture powered by Groq to answer complex natural language questions, compare year-over-year risks, and scan for litigation across companies.

## Features

- **Natural Language Q&A:** Ask company-specific questions based purely on their 10-K filings.
- **Year-over-Year Risk Factor Comparison:** Diff risk factors across years for the same company to track emerging risks.
- **Cross-Company Litigation Scan:** Search across all ingested companies' Legal Proceedings (Item 3) sections.
- **Evidence-Grounded:** All responses are based strictly on the retrieved filings and cite their sources.

## Tech Stack

- **Backend:** Python, FastAPI, Uvicorn
- **Data Ingestion:** BeautifulSoup, lxml, Requests (for SEC EDGAR extraction)
- **Embeddings:** `sentence-transformers` (`all-MiniLM-L6-v2`)
- **Vector Database:** ChromaDB (persistent local)
- **LLM API:** Groq (`openai/gpt-oss-20b`)

## Setup Instructions

1. **Clone the repository.**
2. **Create a virtual environment** and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```
3. **Set up Environment Variables:**
   Copy `.env.example` to `.env` and fill in your Groq API key.
   ```bash
   cp .env.example .env
   ```
4. **Run the API server:**
   ```bash
   uvicorn app.main:app --reload
   ```
5. **Access the API Documentation:**
   Visit `http://localhost:8000/docs` to see the interactive Swagger UI and test the endpoints.

## API Endpoints

- `GET /health` - System status
- `GET /companies` - List available ingested companies and their filing years
- `POST /ask` - RAG Question & Answering for a specific company
- `POST /diff` - Compare risk factors between two years
- `POST /litigation` - Scan for litigation across companies

## Ingestion (Optional)

The repository comes pre-loaded with a ChromaDB containing filings for AAPL, MSFT, and TSLA. If you wish to ingest more companies, you can use the script in the `ingestion/` directory:

```bash
python ingestion/ingest_company.py <TICKER>
```

Note: This will download SEC filings, extract the text, generate embeddings locally, and save them to `./chroma_db`.

## Limitations

- The SEC filing extractor uses heuristic regex parsing for HTML. Certain edge cases in highly custom SEC filings might fail extraction.
- To prevent huge context limits, Year-over-Year diffs use a chunked map-reduce summarization strategy.
>>>>>>> c4e6979 (Update project README and documentation)
