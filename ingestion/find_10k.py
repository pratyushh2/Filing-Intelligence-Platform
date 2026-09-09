import requests

headers = {"User-Agent": "Pratyush pratyushh0212@gmail.com"}

url = "https://data.sec.gov/submissions/CIK0000320193.json"
data = requests.get(url, headers=headers).json()

recent = data["filings"]["recent"]

for i in range(len(recent["form"])):
    if recent["form"][i] == "10-K":
        print("Accession number:", recent["accessionNumber"][i])
        print("Filing date:", recent["filingDate"][i])
        print("Document:", recent["primaryDocument"][i])
        break