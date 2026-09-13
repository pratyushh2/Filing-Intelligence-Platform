# SEC EDGAR Filing Intelligence Platform

This project is an AI-powered SEC EDGAR 10-K Filing Intelligence Platform. It extracts important sections from 10-K filings (Risk Factors and Legal Proceedings), stores them using local embeddings in ChromaDB, and uses a Retrieval-Augmented Generation (RAG) architecture powered by Groq to answer complex natural language questions, compare year-over-year risks, and scan for litigation across companies.
Features

* Natural Language Q&A: Ask company-specific questions based purely on their 10-K filings.
* Year-over-Year Risk Factor Comparison: Diff risk factors across years for the same company to track emerging risks.
* Cross-Company Litigation Scan: Search across all ingested companies' Legal Proceedings (Item 3) sections.
* Evidence-Grounded: All responses are based strictly on the retrieved filings and cite their sources.

🛠️ Tech Stack
| Layer            | Technologies                               |
| ---------------- | ------------------------------------------ |
| 🎨 Frontend      | React, TypeScript, Vite, Tailwind CSS      |
| ⚡ Backend        | Python, FastAPI, Uvicorn                   |
| 📥 Ingestion     | SEC EDGAR, Requests, BeautifulSoup, lxml   |
| 🧮 Embeddings    | Sentence Transformers (`all-MiniLM-L6-v2`) |
| 🗄️ Vector Store | ChromaDB                                   |
| 🤖 LLM           | Groq (`openai/gpt-oss-20b`)                |


Setup Instructions

1. Clone the repository.
2. Create a virtual environment and install dependencies:

```
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

3. Set up Environment Variables: Copy `.env.example` to `.env` and fill in your Groq API key.

```
cp .env.example .env
```

4. Run the API server:

```
uvicorn app.main:app --reload
```

5. Access the API Documentation: Visit `http://localhost:8000/docs` to see the interactive Swagger UI and test the endpoints.

API Endpoints

| Method | Endpoint      | Description                           |
| ------ | ------------- | ------------------------------------- |
| `GET`  | `/health`     | ❤️ System health                      |
| `GET`  | `/companies`  | 🏢 Indexed companies and filing years |
| `POST` | `/ask`        | 🔎 Filing Q&A                         |
| `POST` | `/diff`       | 🔄 Compare risk factors               |
| `POST` | `/litigation` | ⚖️ Cross-company litigation scan      |

Example — /ask
{
  "ticker": "NVDA",
  "text": "What are NVIDIA's biggest business risks?"
}

The response includes the generated answer and the filing sources used to ground it.

📥 Ingest More Companies
python ingestion/ingest_company.py <TICKER>

The ingestion pipeline downloads SEC filings, extracts the relevant sections, generates embeddings locally, and stores them in ./chroma_db.

The current index includes multiple companies such as:

AAPL · AMZN · GOOGL · JPM · KO · META · MSFT · NFLX · NVDA · ORCL · TSLA · WMT

⚠️ Limitations
Section extraction uses heuristic HTML/regex parsing, so unusually formatted SEC filings may require additional extraction rules.
The current pipeline focuses on Item 1A and Item 3 rather than the complete contents of every 10-K.
Year-over-year comparisons use chunked map-reduce summarization to stay within LLM context and token limits.
ChromaDB is currently configured as a persistent local vector store.

🔮 Roadmap
 Support additional SEC filing sections and filing types such as 10-Q and 8-K
 Improve citation granularity with direct filing locations
 Configurable embedding models
 Production-ready managed vector storage
 
📜 License

This project is intended for educational and portfolio use.


* The SEC filing extractor uses heuristic regex parsing for HTML. Certain edge cases in highly custom SEC filings might fail extraction.
* To prevent huge context limits, Year-over-Year diffs use a chunked map-reduce summarization strategy.
