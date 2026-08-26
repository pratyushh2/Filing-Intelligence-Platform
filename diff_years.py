import sys
import os
import time
from dotenv import load_dotenv
import chromadb
from groq import Groq, RateLimitError

load_dotenv()
db_client = chromadb.PersistentClient(path="./chroma_db")
collection = db_client.get_or_create_collection(name="filings")
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def get_full_text_for_year(ticker, year):
    results = collection.get(
        where={"$and": [{"ticker": ticker.upper()}, {"fiscal_year": year}]}
    )
    return "\n".join(results["documents"])


def summarize_chunk(text_chunk, year, retries=3):
    prompt = f"""Summarize the key risk factors mentioned in this excerpt from a {year} 10-K filing. List them as concise bullet points, staying strictly factual to what's written — do not invent details.

Excerpt:
{text_chunk}

Bullet point summary:"""

    for attempt in range(retries):
        try:
            response = groq_client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except RateLimitError:
            print(f"    Rate limited, waiting 10s (attempt {attempt+1}/{retries})...")
            time.sleep(10)

    return "[Summary unavailable due to rate limiting]"


def summarize_full_year(ticker, year, piece_size=6000):
    full_text = get_full_text_for_year(ticker, year)
    if not full_text:
        return None

    pieces = [full_text[i:i+piece_size] for i in range(0, len(full_text), piece_size)]

    piece_summaries = []
    for i, piece in enumerate(pieces):
        print(f"  Summarizing piece {i+1}/{len(pieces)}...")
        summary = summarize_chunk(piece, year)
        piece_summaries.append(summary)
        time.sleep(3)

    return "\n".join(piece_summaries)


def condense_summary(piece_summaries_text, year, max_chars=4000):
    if len(piece_summaries_text) <= max_chars:
        return piece_summaries_text

    prompt = f"""The following are multiple bullet-point summaries covering different parts of a company's {year} Risk Factors section. Condense them into a single, non-repetitive bullet-point list covering all distinct risks mentioned, staying strictly factual.

{piece_summaries_text}

Condensed bullet list:"""

    for attempt in range(3):
        try:
            response = groq_client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except RateLimitError:
            print(f"    Rate limited during condensing, waiting 10s...")
            time.sleep(10)

    return piece_summaries_text[:max_chars]


def diff_years(ticker, year_a, year_b):
    print(f"Summarizing {ticker} {year_a}...")
    raw_summary_a = summarize_full_year(ticker, year_a)
    print(f"Summarizing {ticker} {year_b}...")
    raw_summary_b = summarize_full_year(ticker, year_b)

    if not raw_summary_a or not raw_summary_b:
        return f"Missing data for {ticker} in {year_a} or {year_b} — check ingestion."

    print(f"Condensing {year_a} summary...")
    summary_a = condense_summary(raw_summary_a, year_a)
    time.sleep(3)
    print(f"Condensing {year_b} summary...")
    summary_b = condense_summary(raw_summary_b, year_b)
    time.sleep(3)

    prompt = f"""Compare these two bullet-point summaries of {ticker}'s Risk Factors, from {year_a} and {year_b}. List what appears newly added, removed, or meaningfully changed. Stay strictly factual — do not invent items not present in the summaries.

{year_a} summary:
{summary_a}

{year_b} summary:
{summary_b}

Summary of changes:"""

    for attempt in range(3):
        try:
            response = groq_client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except RateLimitError:
            print(f"Rate limited on final diff, waiting 10s...")
            time.sleep(10)

    return "Failed after retries — try again in a minute."


if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    year_a = sys.argv[2] if len(sys.argv) > 2 else "2023"
    year_b = sys.argv[3] if len(sys.argv) > 3 else "2024"
    result = diff_years(ticker, year_a, year_b)
    print(result)