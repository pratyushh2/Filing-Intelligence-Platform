# 📄 SEC EDGAR Filing Intelligence Platform

> **Turn lengthy SEC 10-K filings into searchable, grounded intelligence.**

An AI-powered platform for analyzing SEC 10-K filings. It extracts high-value sections such as **Risk Factors (Item 1A)** and **Legal Proceedings (Item 3)**, generates local embeddings, and uses a **Retrieval-Augmented Generation (RAG)** pipeline powered by Groq to answer natural-language questions, compare year-over-year risks, and scan for litigation across companies — all grounded in the actual filing text.

## ✨ Features

- 🔎 **Natural Language Q&A** — Ask company-specific questions answered from 10-K filings.
- ⚠️ **Year-over-Year Risk Comparison** — Compare Risk Factors across filing years to identify emerging or changing risks.
- ⚖️ **Cross-Company Litigation Scan** — Search Legal Proceedings (Item 3) across indexed companies.
- 📚 **Evidence-Grounded Answers** — Responses are generated from retrieved filing text with source references.
- 🏢 **Multi-Company Analysis** — Query filings across a centralized ChromaDB index.
- 💬 **Interactive Web Interface** — React-based frontend for exploring companies and filing insights.

## 🧠 Architecture

```text
                    SEC EDGAR
                        │
                        ▼
              Filing Extraction
            (BeautifulSoup / lxml)
                        │
                        ▼
              Section Parser
              ┌─────────┴─────────┐
              ▼                   ▼
        Item 1A Risk         Item 3 Legal
           Factors           Proceedings
              │                   │
              └─────────┬─────────┘
                        ▼
               Chunking + Embeddings
             (all-MiniLM-L6-v2)
                        │
                        ▼
                   ChromaDB
               Persistent Vector Store
                        │
                        ▼
                Semantic Retrieval
                        │
                        ▼
                  Groq LLM
             (openai/gpt-oss-20b)
                        │
                        ▼
                FastAPI Backend
              /ask /diff /litigation
                        │
                        ▼
              React + TypeScript UI

🛠️ Tech Stack
Layer	Technologies
🎨 Frontend	React, TypeScript, Vite, Tailwind CSS
⚡ Backend	Python, FastAPI, Uvicorn
📥 Ingestion	SEC EDGAR, Requests, BeautifulSoup, lxml
🧮 Embeddings	Sentence Transformers (all-MiniLM-L6-v2)
🗄️ Vector Store	ChromaDB
🤖 LLM	Groq (openai/gpt-oss-20b)

🚀 Quickstart
1. Clone the repository
git clone https://github.com/pratyushh2/Filing-Intelligence-Platform.git
cd Filing-Intelligence-Platform
2. Backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt

Create .env from .env.example and add your Groq API key.

cp .env.example .env

Start the API:

uvicorn app.main:app --reload

API: http://localhost:8000

Swagger UI: http://localhost:8000/docs

3. Frontend
cd frontend
npm install
npm run dev

Configure the backend URL in the frontend environment:

VITE_API_BASE_URL=http://127.0.0.1:8000
🔌 API
Method	Endpoint	Description
GET	/health	❤️ System health
GET	/companies	🏢 Indexed companies and filing years
POST	/ask	🔎 Filing Q&A
POST	/diff	🔄 Compare risk factors
POST	/litigation	⚖️ Cross-company litigation scan
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
