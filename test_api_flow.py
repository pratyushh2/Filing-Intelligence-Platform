import sys
import requests
import json

sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

def test_ask(ticker, question, label=""):
    print(f"\n==========================================")
    print(f"[{label}] Ticker: {ticker} | Question: {question}")
    resp = requests.post(f"{BASE_URL}/ask", json={"ticker": ticker, "text": question}, timeout=30)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Ticker returned: {data.get('ticker')}")
        print(f"Sources returned: {len(data.get('sources', []))}")
        for idx, s in enumerate(data.get('sources', [])[:3]):
            print(f"  Source {idx+1}: {s.get('ticker')} {s.get('fiscal_year')} {s.get('section')} (URL: {s.get('source_url')})")
        print(f"Answer:\n{data.get('answer', '')}\n")
    else:
        print(f"Error: {resp.text}")

if __name__ == "__main__":
    print("Checking Health:")
    h = requests.get(f"{BASE_URL}/health").json()
    print(json.dumps(h, indent=2))

    # 6 Specified Questions
    test_ask("NVDA", "What are NVIDIA's biggest business risks disclosed in its latest 10-K?", "TEST 1")
    test_ask("NVDA", "What cybersecurity risks does NVIDIA disclose?", "TEST 2")
    test_ask("NVDA", "What supply-chain and manufacturing risks does NVIDIA face?", "TEST 3")
    test_ask("NVDA", "What are 10-K filings?", "TEST 4")
    test_ask("NVDA", "What regulatory risks does NVIDIA face regarding AI and export controls?", "TEST 5")
    test_ask("NVDA", "According to NVIDIA's 2025 10-K, what risks are associated with export controls on advanced computing products?", "TEST 6")

    # Company Isolation
    test_ask("MSFT", "What are Microsoft's biggest business risks disclosed in its latest 10-K?", "COMPANY ISOLATION: MSFT")
    test_ask("AAPL", "What are Apple's biggest business risks disclosed in its latest 10-K?", "COMPANY ISOLATION: AAPL")
