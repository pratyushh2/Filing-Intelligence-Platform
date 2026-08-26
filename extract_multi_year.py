from bs4 import BeautifulSoup
import re
import os

pattern = re.compile(r"Item\s+1A\.?\s+Risk Factors", re.IGNORECASE)
end_pattern = re.compile(r"Item\s+1B\.?", re.IGNORECASE)

for filename in os.listdir("filings"):
    year = filename.replace("aapl_10k_", "").replace(".html", "")

    with open(f"filings/{filename}", "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text(separator="\n")

    match = pattern.search(text)
    if not match:
        print(f"Couldn't find Item 1A for {year}")
        continue

    start = match.start()
    end_match = end_pattern.search(text, start + 100)
    end = end_match.start() if end_match else start + 20000

    risk_section = text[start:end]

    with open(f"filings/risk_{year}.txt", "w", encoding="utf-8") as f:
        f.write(risk_section)

    print(f"Extracted risk factors for {year}")