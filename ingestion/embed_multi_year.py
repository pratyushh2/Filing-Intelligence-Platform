from sentence_transformers import SentenceTransformer
import chromadb
import os

model = SentenceTransformer("all-MiniLM-L6-v2")
db_client = chromadb.PersistentClient(path="./chroma_db")
collection = db_client.get_or_create_collection(name="filings")

def chunk_text(text, chunk_size=800, overlap=100):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks

for filename in os.listdir("filings"):
    if not filename.startswith("risk_"):
        continue

    year = filename.replace("risk_", "").replace(".txt", "")

    with open(f"filings/{filename}", "r", encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_text(text)

    for i, chunk in enumerate(chunks):
        embedding = model.encode(chunk).tolist()
        collection.add(
            ids=[f"aapl_10k_{year}_riskfactors_{i}"],
            embeddings=[embedding],
            documents=[chunk],
            metadatas=[{
                "ticker": "AAPL",
                "filing_type": "10-K",
                "fiscal_year": year,
                "section": "Item 1A"
            }]
        )

    print(f"Embedded {len(chunks)} chunks for {year}")