import chromadb

db_client = chromadb.PersistentClient(path="./chroma_db")
collection = db_client.get_or_create_collection(name="filings")

results = collection.get(where={"ticker": "TSLA"}, limit=5)

print("Number of TSLA chunks found:", len(results["documents"]))
if results["documents"]:
    print("\nSample chunk:")
    print(results["documents"][0][:300])
    print("\nSample metadata:")
    print(results["metadatas"][0])