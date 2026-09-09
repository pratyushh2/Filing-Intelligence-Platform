from bs4 import BeautifulSoup
import re

with open("apple_10k.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "lxml")
text = soup.get_text(separator="\n")

# Find where "Item 1A" starts and "Item 1B" (or Item 2) starts — that boundary is our section
pattern = re.compile(r"Item\s+1A\.?\s+Risk Factors", re.IGNORECASE)
match = pattern.search(text)

if match:
    start = match.start()
    end_pattern = re.compile(r"Item\s+1B\.?", re.IGNORECASE)
    end_match = end_pattern.search(text, start + 100)
    end = end_match.start() if end_match else start + 20000

    risk_section = text[start:end]
    print(risk_section[:1000])  # print first 1000 characters as a preview

    with open("risk_factors.txt", "w", encoding="utf-8") as f:
        f.write(risk_section)
else:
    print("Couldn't find Item 1A — the formatting on this filing is different, we'll need to adjust the pattern.")