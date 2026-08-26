import chromadb

db_client = chromadb.PersistentClient(path="./chroma_db")
collection = db_client.get_or_create_collection(name="filings")

results = collection.get(where={"ticker": "AAPL"})

years_found = set()
for metadata in results["metadatas"]:
    years_found.add(metadata["fiscal_year"])

print("Years found in database:", years_found)
print("Total chunks:", len(results["documents"]))