from edgar_utils import get_cik, get_recent_10ks, fetch_filing_html, extract_risk_factors
import re

cik = get_cik("MSFT")
filings = get_recent_10ks(cik, limit=1)
filing = filings[0]

html = fetch_filing_html(cik, filing["accession"], filing["document"])

from bs4 import BeautifulSoup
soup = BeautifulSoup(html, "lxml")
text = soup.get_text(separator="\n")

pattern = re.compile(r"Item\s+1A\.?\s+Risk Factors", re.IGNORECASE)
end_pattern = re.compile(r"Item\s+1B\.?", re.IGNORECASE)

matches = list(pattern.finditer(text))
print(f"Found {len(matches)} matches for 'Item 1A Risk Factors'")

for m in matches:
    start = m.start()
    end_match = end_pattern.search(text, m.end())
    end = end_match.start() if end_match else start + 20000
    length = end - start
    print(f"Match at {start}, length {length}")
    print("Preview:", text[start:start+150].replace("\n", " "))
    print("---")

    # Find every occurrence of "RISK FACTORS" (case-insensitive) anywhere in the doc
import re
all_occurrences = [m.start() for m in re.finditer(r"RISK FACTORS", text, re.IGNORECASE)]
print(f"\n'RISK FACTORS' appears {len(all_occurrences)} times total, at positions: {all_occurrences}")

for pos in all_occurrences:
    print(f"\n--- At position {pos} ---")
    print(text[pos-150:pos+150].replace("\n", " | "))