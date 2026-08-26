from sentence_transformers import SentenceTransformer
import chromadb

model = SentenceTransformer("all-MiniLM-L6-v2")

db_client = chromadb.PersistentClient(path="./chroma_db")
collection = db_client.get_or_create_collection(name="filings")

query = "What supply chain risks does Apple face?"
query_embedding = model.encode(query).tolist()

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3
)

for doc in results["documents"][0]:
    print(doc[:300])
    print("---")