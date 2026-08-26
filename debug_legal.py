from edgar_utils import get_cik, get_recent_10ks, fetch_filing_html
from bs4 import BeautifulSoup
import re

cik = get_cik("MSFT")
filings = get_recent_10ks(cik, limit=1)
filing = filings[0]

html = fetch_filing_html(cik, filing["accession"], filing["document"])
soup = BeautifulSoup(html, "lxml")
text = soup.get_text(separator="\n")

all_occurrences = [m.start() for m in re.finditer(r"Legal Proceedings", text, re.IGNORECASE)]
print(f"'Legal Proceedings' appears {len(all_occurrences)} times, at positions: {all_occurrences}")

for pos in all_occurrences:
    print(f"\n--- At position {pos} ---")
    print(text[pos-100:pos+250].replace("\n", " | "))