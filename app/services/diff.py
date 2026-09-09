import time
import json
from app.services.db import get_collection
from app.services.groq_service import get_groq_completion
from app.models import DiffRequest, DiffResponse, DiffChange, Source
import logging

logger = logging.getLogger(__name__)

def get_full_text_for_year(ticker: str, year: str) -> str:
    collection = get_collection()
    results = collection.get(
        where={"$and": [{"ticker": ticker.upper()}, {"fiscal_year": str(year)}, {"section": "Item 1A"}]}
    )
    if not results or not results["documents"]:
        return ""
    return "\n".join(results["documents"])

def summarize_chunk(text_chunk: str, year: str) -> str:
    prompt = f"""Summarize the key risk factors mentioned in this excerpt from a {year} 10-K filing. List them as concise bullet points, staying strictly factual to what's written — do not invent details.

Excerpt:
{text_chunk}

Bullet point summary:"""
    
    return get_groq_completion(prompt)

def summarize_full_year(ticker: str, year: str, piece_size: int = 6000) -> str:
    full_text = get_full_text_for_year(ticker, year)
    if not full_text:
        return ""

    pieces = [full_text[i:i+piece_size] for i in range(0, len(full_text), piece_size)]

    piece_summaries = []
    for i, piece in enumerate(pieces):
        logger.info(f"Summarizing piece {i+1}/{len(pieces)} for {ticker} {year}")
        summary = summarize_chunk(piece, year)
        piece_summaries.append(summary)
        if i < len(pieces) - 1:  # No need to sleep after last piece
            time.sleep(8)  # 8s gap: keeps us well under Groq's token/min limit

    return "\n".join(piece_summaries)

def condense_summary(piece_summaries_text: str, year: str, max_chars: int = 4000) -> str:
    if len(piece_summaries_text) <= max_chars:
        return piece_summaries_text

    prompt = f"""The following are multiple bullet-point summaries covering different parts of a company's {year} Risk Factors section. Condense them into a single, non-repetitive bullet-point list covering all distinct risks mentioned, staying strictly factual.

{piece_summaries_text}

Condensed bullet list:"""

    return get_groq_completion(prompt)

def diff_years(request: DiffRequest) -> DiffResponse:
    ticker = request.ticker.upper()
    
    if request.year1 == request.year2:
        raise ValueError("year1 and year2 must be different.")
    
    # 1. Summarize Year A
    raw_summary_a = summarize_full_year(ticker, request.year1)
    if not raw_summary_a:
        raise ValueError(f"Missing data for {ticker} in {request.year1}")

    # Cool down between the two year summarizations to avoid rate limit accumulation
    logger.info(f"Year 1 summarized. Cooling down 20s before year 2...")
    time.sleep(20)

    # 2. Summarize Year B
    raw_summary_b = summarize_full_year(ticker, request.year2)
    if not raw_summary_b:
        raise ValueError(f"Missing data for {ticker} in {request.year2}")

    # 3. Condense
    summary_a = condense_summary(raw_summary_a, request.year1)
    summary_b = condense_summary(raw_summary_b, request.year2)

    # 4. Diff
    prompt = f"""Compare these two bullet-point summaries of {ticker}'s Risk Factors, from {request.year1} and {request.year2}. 
Identify what appears newly added, removed, or meaningfully changed. Stay strictly factual — do not invent items not present in the summaries.
If the model cannot establish a change from the provided filing content, state it clearly in the summary.

You must reply ONLY with a valid JSON object matching this schema. Do not include any intro, outro, or markdown formatting.
{{
  "summary": "Overall summary of changes",
  "changes": [
    {{
      "type": "added|removed|changed",
      "topic": "Short topic of the risk",
      "description": "Detailed description of what changed"
    }}
  ]
}}

{request.year1} summary:
{summary_a}

{request.year2} summary:
{summary_b}
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
        sources=[]  # We omit sources for diff because it comes from many chunks, but could add if needed
    )
