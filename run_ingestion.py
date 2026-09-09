import sys
import time
import chromadb
from collections import defaultdict
import os

# add ingestion dir to path so we can import
sys.path.append(os.path.join(os.path.dirname(__file__), "ingestion"))
from ingest_company import ingest

def run():
    target_companies = ["NVDA", "AMZN", "GOOGL", "META", "JPM", "KO", "WMT", "NFLX", "ORCL"]
    
    db_client = chromadb.PersistentClient(path="./chroma_db")
    collection = db_client.get_or_create_collection(name="filings")
    
    total_chunks_before = collection.count()
    print(f"Total chunks before ingestion: {total_chunks_before}")
    
    # Check what is already present to see if we should skip anything?
    # Actually the user asked NOT to re-ingest AAPL/MSFT/TSLA unnecessarily. We'll just run ingest for the target list which excludes those.
    
    failed_companies = []
    
    for ticker in target_companies:
        print(f"--- Ingesting {ticker} ---")
        try:
            ingest(ticker)
        except Exception as e:
            print(f"Failed {ticker}: {e}")
            failed_companies.append(ticker)
        time.sleep(1) # Respect rate limits somewhat

    total_chunks_after = collection.count()
    print(f"Total chunks after ingestion: {total_chunks_after}")
    
    # Generate report
    result = collection.get(include=["metadatas"])
    metadatas = result["metadatas"]
    ids = result["ids"]
    
    companies_present = set()
    years_per_company = defaultdict(set)
    chunk_count_per_company = defaultdict(int)
    item_1a_count = defaultdict(int)
    item_3_count = defaultdict(int)
    
    for i, meta in enumerate(metadatas):
        ticker = meta["ticker"]
        year = meta["fiscal_year"]
        section = meta["section"]
        
        companies_present.add(ticker)
        years_per_company[ticker].add(year)
        chunk_count_per_company[ticker] += 1
        
        if section == "Item 1A":
            item_1a_count[ticker] += 1
        elif section == "Item 3":
            item_3_count[ticker] += 1
            
    print("\n--- FINAL REPORT ---")
    print(f"Total chunks before: {total_chunks_before}")
    print(f"Total chunks after: {total_chunks_after}")
    print(f"Companies in DB: {sorted(list(companies_present))}")
    print("\nYears present:")
    for c in sorted(companies_present):
        print(f"  {c}: {sorted(list(years_per_company[c]))}")
        
    print("\nChunk count per company:")
    for c in sorted(companies_present):
        print(f"  {c}: {chunk_count_per_company[c]} total (Item 1A: {item_1a_count[c]}, Item 3: {item_3_count[c]})")
        
    print(f"\nDuplicates Check: Total IDs = {len(ids)}, Unique IDs = {len(set(ids))}")
    if len(ids) == len(set(ids)):
        print("  -> No duplicate IDs detected (Idempotency check passed).")
    else:
        print("  -> Duplicate IDs detected!")
        
    if failed_companies:
        print(f"\nFailed Companies: {failed_companies}")
    else:
        print("\nNo companies failed.")
        
if __name__ == '__main__':
    run()
