import requests

headers = {"User-Agent": "Pratyush pratyushh0212@gmail.com"}

cik = "320193"
accession = "0000320193-25-000079"  # paste the one you got from find_10k.py
accession_nodash = accession.replace("-", "")
doc = "aapl-20250927.htm"  # paste the primaryDocument value you got

url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_nodash}/{doc}"
response = requests.get(url, headers=headers)

with open("apple_10k.html", "w", encoding="utf-8") as f:
    f.write(response.text)

print("Saved! File size:", len(response.text), "characters")