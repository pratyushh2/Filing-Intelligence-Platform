import sys
import chromadb

db_client = chromadb.PersistentClient(path="./chroma_db")
collection = db_client.get_or_create_collection(name="filings")

ticker = sys.argv[1] if len(sys.argv) > 1 else "MSFT"
section = sys.argv[2] if len(sys.argv) > 2 else "Item 3"

results = collection.get(
    where={"$and": [{"ticker": ticker}, {"section": section}]}
)

print(f"Found {len(results['documents'])} chunks for {ticker} / {section}")
if results["documents"]:
    print("\nFull first chunk:")
    print(results["documents"][0])