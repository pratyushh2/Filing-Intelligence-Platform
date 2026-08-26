Filing Intelligence Platform — Full Project Specification
1. Project Description

Filing Intelligence Platform is a Retrieval-Augmented Generation (RAG) system built on top of the U.S. Securities and Exchange Commission's EDGAR database. It ingests public companies' 10-K filings (annual reports), extracts the two most analytically valuable narrative sections — Item 1A (Risk Factors) and Item 3 (Legal Proceedings) — and makes that information queryable through natural language, instead of requiring a human to manually read hundred-page legal documents.

The platform combines three distinct analytical capabilities on top of one shared data pipeline:

Natural-language Q&A over any ingested company's most recent risk disclosures, with answers grounded strictly in the actual filing text (not the AI's general knowledge).
Year-over-year risk factor diffing — automatically summarizing what risk language a company added, removed, or meaningfully reworded between two fiscal years, surfacing shifts in a company's own stated risk posture over time.
Cross-company litigation scanning — semantic search across the Legal Proceedings sections of multiple companies at once, so a user can ask questions like "which companies disclose antitrust litigation?" without reading each filing individually.

The system is built entirely on free-tier infrastructure: EDGAR's public APIs for data, local (on-device) sentence-embedding models for semantic search, ChromaDB as the vector store, and Groq's free-tier LLM API for generation — meaning it can be run, demonstrated, and eventually hosted with no ongoing API costs.

2. Who This Is For, and Why It's Useful
User type	Use case	Value delivered
Retail/individual investors	Understanding what risks a company they're invested in (or considering investing in) actually discloses, without reading a 100+ page legal document	Plain-language answers to specific questions, grounded in the real filing
Finance/equity research students	Learning to compare how companies frame risk, or how a single company's risk language evolves	Fast comparative analysis that would normally take hours of manual reading
Junior analysts / paralegals	Quickly triaging which companies in a sector disclose a specific type of legal exposure (e.g., antitrust, IP litigation)	Cross-company search that would otherwise mean opening dozens of individual filings
Portfolio/project reviewers (recruiters, interviewers)	Evaluating a demonstrable, technically substantive AI/ML/RAG project	A working system that shows real engineering judgment — not just an API wrapper, but a pipeline that handles real-world data messiness

The core value proposition: SEC filings are public, free, and information-dense — but functionally inaccessible to most people because of their length and legal density. This project makes that information queryable in plain English, with every answer traceable back to a real, specific source document.

3. How It Works — Full System Logic
3.1 Data ingestion layer
User (or system) provides a stock ticker (e.g., "AAPL").
get_cik() resolves the ticker to the SEC's internal company identifier (CIK) via EDGAR's public ticker-to-CIK mapping file.
get_recent_10ks() calls EDGAR's submissions API to retrieve a company's filing history and identifies the most recent N annual reports (10-Ks).
fetch_filing_html() downloads the raw HTML of each filing directly from EDGAR's archive.
3.2 Section extraction layer
Raw 10-K HTML is parsed with BeautifulSoup into plain text.
Two target sections are located using regex pattern matching with a disambiguation heuristic:
Every 10-K contains multiple mentions of section headings like "Item 1A" and "Legal Proceedings" — in the table of contents, in cross-references, and in the real section itself. A naive first-match approach incorrectly grabs the table-of-contents entry.
The system instead finds every candidate match, measures the text distance to the next section boundary for each, and selects the candidate with the largest gap — since the real section always contains far more content than a compact ToC listing or a one-line cross-reference.
Two heading-format patterns are checked per section (e.g., "Item 1A. Risk Factors" as one phrase, vs. "PART I" followed by "Item 1A" as separate elements), since different companies format their filings differently (discovered empirically: Apple and Tesla use the former style, Microsoft uses the latter).
Sections under a minimum length threshold are treated as redirect notices (e.g., some companies write "see Note X of our financial statements" instead of substantive Item 3 content) and are skipped rather than stored as misleading fragments.
3.3 Chunking and embedding layer
Extracted section text is split into overlapping ~800-character chunks (100-character overlap, so sentences aren't cut off at chunk boundaries and lose context).
Each chunk is converted into a vector embedding using a local, free sentence-embedding model (all-MiniLM-L6-v2 via sentence-transformers) — no external API call or cost required for this step.
Each embedded chunk is stored in a persistent ChromaDB vector database, tagged with metadata: ticker, filing_type, fiscal_year, section. This metadata is what enables filtered retrieval later (e.g., "only AAPL," "only Item 3," "only fiscal year 2024").
3.4 Retrieval + generation layer (the "RAG" core)
Mode 1 (Q&A): A user's question is embedded the same way as the stored chunks. Chroma's similarity search finds the most semantically relevant chunks for a specific company (filtered by ticker). Those chunks are inserted into a prompt instructing the LLM (via Groq, model openai/gpt-oss-20b) to answer using only the provided context — this is the core discipline that keeps answers grounded rather than hallucinated.
Mode 2 (Risk Diff): Rather than similarity search, this mode does an exact metadata-filtered fetch — retrieving all chunks for a given company and fiscal year (not just the top-k most similar). Because full-year sections can exceed the LLM's per-request token limit, a map-reduce summarization pattern is used: each chunk is summarized individually, per-year summaries are combined and (if still too large) condensed again, and finally the two years' condensed summaries are diffed by the LLM, which is instructed to identify additions, removals, and reworded language while staying strictly factual.
Mode 3 (Litigation Scan): A user's query (e.g., "which companies mention antitrust risk?") is embedded and matched against Item 3 chunks across all ingested companies simultaneously (filtered only by section, not by ticker). Retrieved chunks are labeled with their source company/year before being handed to the LLM, which is instructed to cite which company each point comes from and never speculate about companies not present in the retrieved context.
3.5 Serving layer
A FastAPI backend exposes each mode as a REST endpoint (/ask, and equivalents to be built for diff and litigation scan), accepting JSON requests and returning JSON responses.
A Streamlit frontend (to be replaced/styled by the user) provides a browser-based interface that calls these endpoints.
3.6 Known, documented limitations (important for honest scope)
Extraction relies on heuristic pattern matching, not a structured/guaranteed schema — it has been tested and hardened against three real companies' distinct formatting styles (Apple, Microsoft, Tesla) but may fail on smaller, older, or unusually-formatted filers.
Some companies' Item 3 sections are legitimately sparse (they redirect to financial statement notes) — this is correctly detected and skipped, not a bug, but it does mean litigation coverage is inherently uneven across companies by design of the filings themselves.
Free-tier LLM usage (Groq) is subject to per-minute token rate limits, requiring retry/pacing logic already built into the diffing pipeline.
