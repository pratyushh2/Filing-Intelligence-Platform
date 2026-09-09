from bs4 import XMLParsedAsHTMLWarning
import warnings
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
import requests

HEADERS = {"User-Agent": "Pratyush pratyushh0212@gmail.com"}

def get_cik(ticker):
    url = "https://www.sec.gov/files/company_tickers.json"
    data = requests.get(url, headers=HEADERS).json()

    ticker = ticker.upper()
    for entry in data.values():
        if entry["ticker"] == ticker:
            cik = str(entry["cik_str"]).zfill(10)
            return cik

    return None

from bs4 import BeautifulSoup
import re
import os

def get_recent_10ks(cik, limit=4):
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    data = requests.get(url, headers=HEADERS).json()
    recent = data["filings"]["recent"]

    filings = []
    for i in range(len(recent["form"])):
        if recent["form"][i] == "10-K" and len(filings) < limit:
            filings.append({
                "accession": recent["accessionNumber"][i],
                "document": recent["primaryDocument"][i],
                "year": recent["filingDate"][i][:4]
            })
    return filings

def fetch_filing_html(cik, accession, document):
    accession_nodash = accession.replace("-", "")
    url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_nodash}/{document}"
    response = requests.get(url, headers=HEADERS)
    return response.text

def extract_risk_factors(html):
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text(separator="\n")

    pattern_a = re.compile(r"Item\s+1A\.?\s+Risk Factors", re.IGNORECASE)
    pattern_b = re.compile(r"PART\s+I\s+Item\s+1A\b", re.IGNORECASE)
    end_pattern = re.compile(r"Item\s+1B\.?", re.IGNORECASE)

    matches = list(pattern_a.finditer(text)) + list(pattern_b.finditer(text))

    if not matches:
        return None

    best_section = None
    best_length = 0

    for m in matches:
        start = m.start()
        end_match = end_pattern.search(text, m.end())
        end = end_match.start() if end_match else start + 20000
        length = end - start

        if length > best_length:
            best_length = length
            best_section = text[start:end]

    return best_section

def extract_legal_proceedings(html):
    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text(separator="\n")

    pattern_a = re.compile(r"Item\s+3\.?\s+Legal Proceedings", re.IGNORECASE)
    pattern_b = re.compile(r"PART\s+I\s+Item\s+3\b", re.IGNORECASE)
    end_pattern = re.compile(r"Item\s+4\.?", re.IGNORECASE)

    matches = list(pattern_a.finditer(text)) + list(pattern_b.finditer(text))

    if not matches:
        return None

    best_section = None
    best_length = 0

    for m in matches:
        start = m.start()
        end_match = end_pattern.search(text, m.end())
        end = end_match.start() if end_match else start + 20000
        length = end - start

        if length > best_length:
            best_length = length
            best_section = text[start:end]

    return best_section