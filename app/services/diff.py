import time
import json
from app.services.db import get_collection
from app.services.groq_service import get_groq_completion
from app.models import DiffRequest, DiffResponse, DiffChange, Source
import logging
import re

logger = logging.getLogger(__name__)

def _extract_chunk_index(chunk_id: str) -> int:
    match = re.search(r"_(\d+)$", chunk_id)
    return int(match.group(1)) if match else 0

def get_full_text_for_year(ticker: str, year: str) -> str:
    collection = get_collection()
    results = collection.get(
        where={"$and": [{"ticker": ticker.upper()}, {"fiscal_year": str(year)}, {"section": "Item 1A"}]}
    )
    if not results or not results.get("documents"):
        return ""

    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])
    ids = results.get("ids", [])

    # Strict secondary verification: only Item 1A for this exact ticker/year
    valid_chunks = []
    for doc_id, doc, meta in zip(ids, documents, metadatas):
        if not doc or not meta:
            continue
        if meta.get("ticker", "").upper() != ticker.upper():
            continue
        if str(meta.get("fiscal_year")) != str(year):
            continue
        if meta.get("section") != "Item 1A":
            continue
        valid_chunks.append((_extract_chunk_index(doc_id), doc))

    if not valid_chunks:
        return ""

    valid_chunks.sort(key=lambda x: x[0])
    return "\n".join(chunk_text for _, chunk_text in valid_chunks)


# Token budget constants for openai/gpt-oss-20b (8000 TPM hard limit)
# 4000 chars ≈ 1000 tokens; prompt overhead ~150 tokens → each summarize call ~1150 tokens
_PIECE_SIZE = 4000
# Max chars of combined summaries fed to condense step (~12000 chars ≈ 3000 tokens + 200 overhead)
_MAX_CONDENSE_INPUT_CHARS = 12000
# Max chars per year summary in the final diff prompt (3000 chars ≈ 750 tokens × 2 years + 300 prompt = ~1800 tokens)
_MAX_DIFF_SUMMARY_CHARS = 3000


def summarize_chunk(text_chunk: str, year: str) -> str:
    # Hard-cap chunk to 4000 chars so with prompt we stay well under 1500 tokens
    safe_chunk = text_chunk[:_PIECE_SIZE]
    prompt = f"""Summarize the key risk factors from this {year} 10-K excerpt.
Be concise: 3-6 bullet points, factual only, no invented details.

Excerpt:
{safe_chunk}

Bullet points:"""
    return get_groq_completion(prompt)


def summarize_full_year(ticker: str, year: str) -> str:
    full_text = get_full_text_for_year(ticker, year)
    if not full_text:
        return ""

    pieces = [full_text[i:i+_PIECE_SIZE] for i in range(0, len(full_text), _PIECE_SIZE)]
    logger.info(f"Summarizing {len(pieces)} pieces for {ticker} {year}")

    piece_summaries = []
    for i, piece in enumerate(pieces):
        logger.info(f"  Piece {i+1}/{len(pieces)} for {ticker} {year}")
        summary = summarize_chunk(piece, year)
        piece_summaries.append(summary)
        if i < len(pieces) - 1:
            time.sleep(12)  # 12s between calls (~5 calls/min) — safe under 8000 TPM

    return "\n".join(piece_summaries)


def condense_summary(piece_summaries_text: str, year: str) -> str:
    """Condense all piece summaries into one bullet list. Hard-truncates input to stay within TPM."""
    truncated = piece_summaries_text[:_MAX_CONDENSE_INPUT_CHARS]

    prompt = f"""Below are bullet-point summaries of parts of a company's {year} Risk Factors (Item 1A).
Merge into ONE concise, non-repetitive bullet list. Max 12 bullets. Factual only.

{truncated}

Condensed risk list:"""
    return get_groq_completion(prompt)


def diff_years(request: DiffRequest) -> DiffResponse:
    ticker = request.ticker.upper()

    if request.year1 == request.year2:
        raise ValueError("year1 and year2 must be different.")

    # 1. Map-reduce summarize Year A
    logger.info(f"Starting summarization for {ticker} {request.year1}")
    raw_summary_a = summarize_full_year(ticker, request.year1)
    if not raw_summary_a:
        raise ValueError(f"Missing data for {ticker} in {request.year1}")

    logger.info("Year 1 done. Cooling down 30s...")
    time.sleep(30)

    # 2. Map-reduce summarize Year B
    logger.info(f"Starting summarization for {ticker} {request.year2}")
    raw_summary_b = summarize_full_year(ticker, request.year2)
    if not raw_summary_b:
        raise ValueError(f"Missing data for {ticker} in {request.year2}")

    # 3. Condense each year
    logger.info("Condensing year A...")
    time.sleep(15)
    summary_a = condense_summary(raw_summary_a, request.year1)
    logger.info("Condensing year B...")
    time.sleep(15)
    summary_b = condense_summary(raw_summary_b, request.year2)
    time.sleep(15)

    # Hard-truncate to keep the final diff prompt under ~2000 tokens total
    summary_a_trunc = summary_a[:_MAX_DIFF_SUMMARY_CHARS]
    summary_b_trunc = summary_b[:_MAX_DIFF_SUMMARY_CHARS]

    # 4. Diff
    prompt = f"""Compare {ticker}'s Risk Factors between {request.year1} and {request.year2}.
Identify risks that are newly added, removed, or meaningfully changed.
Factual only — use only what the summaries say.

Reply ONLY with valid JSON — no markdown, no prose outside the JSON.
{{
  "summary": "2-3 sentence overview of how risks changed between the years",
  "changes": [
    {{
      "type": "added|removed|changed",
      "topic": "Short risk topic name",
      "description": "What changed and why it matters"
    }}
  ]
}}

{request.year1} risk summary:
{summary_a_trunc}

{request.year2} risk summary:
{summary_b_trunc}
"""

    response_json_str = get_groq_completion(prompt)

    # Robustly extract JSON block
    cleaned_json_str = response_json_str.strip()
    start_idx = cleaned_json_str.find('{')
    end_idx = cleaned_json_str.rfind('}')

    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        cleaned_json_str = cleaned_json_str[start_idx:end_idx+1]

    try:
        parsed = json.loads(cleaned_json_str)
        changes = [DiffChange(**c) for c in parsed.get("changes", [])]
        summary = parsed.get("summary", "No summary provided.")
    except Exception as e:
        logger.error(f"Failed to parse JSON from Groq: {e}\nResponse: {response_json_str}")
        changes = []
        summary = "Failed to parse structured changes from model output."

    return DiffResponse(
        ticker=ticker,
        year1=request.year1,
        year2=request.year2,
        summary=summary,
        changes=changes,
        sources=[]
    )
