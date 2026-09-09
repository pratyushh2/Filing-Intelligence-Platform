import requests
import os

headers = {"User-Agent": "YourName youremail@example.com"}

cik = "320193"
url = f"https://data.sec.gov/submissions/CIK0000{cik}.json"
data = requests.get(url, headers=headers).json()

recent = data["filings"]["recent"]

os.makedirs("filings", exist_ok=True)

count = 0
for i in range(len(recent["form"])):
    if recent["form"][i] == "10-K" and count < 4:
        accession = recent["accessionNumber"][i]
        accession_nodash = accession.replace("-", "")
        doc = recent["primaryDocument"][i]
        filing_date = recent["filingDate"][i]
        year = filing_date[:4]

        filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_nodash}/{doc}"
        response = requests.get(filing_url, headers=headers)

        filename = f"filings/aapl_10k_{year}.html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(response.text)

        print(f"Saved {filename}")
        count += 1