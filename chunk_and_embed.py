from sentence_transformers import SentenceTransformer
import chromadb

with open("risk_factors.txt", "r", encoding="utf-8") as f:
    text = f.read()

def chunk_text(text, chunk_size=800, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

chunks = chunk_text(text)
print(f"Split into {len(chunks)} chunks")

model = SentenceTransformer("all-MiniLM-L6-v2")

db_client = chromadb.PersistentClient(path="./chroma_db")
collection = db_client.get_or_create_collection(name="filings")

for i, chunk in enumerate(chunks):
    embedding = model.encode(chunk).tolist()

    collection.add(
        ids=[f"aapl_10k_2024_riskfactors_{i}"],
        embeddings=[embedding],
        documents=[chunk],
        metadatas=[{
            "ticker": "AAPL",
            "filing_type": "10-K",
            "fiscal_year": 2024,
            "section": "Item 1A"
        }]
    )

print("Saved all chunks to the vector database")