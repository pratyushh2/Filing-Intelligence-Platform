import requests

headers = {
    "User-Agent": "Pratyush pratyushh0212@gmail.com"
}

url = "https://data.sec.gov/submissions/CIK0000320193.json"
response = requests.get(url, headers=headers)
data = response.json()

print(data["name"])
print(data["sic"])