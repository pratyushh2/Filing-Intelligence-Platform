import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import chromadb
from groq import Groq, RateLimitError
import time

load_dotenv()

embed_model = SentenceTransformer("all-MiniLM-L6-v2")
db_client = chromadb.PersistentClient(path="./chroma_db")
collection = db_client.get_or_create_collection(name="filings")
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def scan_litigation(query, n_results=8):
    query_embedding = embed_model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where={"section": "Item 3"}
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    if not documents:
        return "No litigation-related disclosures found matching that query."

    context_pieces = []
    for doc, meta in zip(documents, metadatas):
        label = f"[{meta['ticker']} - {meta['fiscal_year']}]"
        context_pieces.append(f"{label}\n{doc}")

    context = "\n\n---\n\n".join(context_pieces)

    prompt = f"""You are a financial analyst assistant. Below are excerpts from Legal Proceedings (Item 3) sections of various companies' 10-K filings, each labeled with the company ticker and fiscal year. Answer the question using ONLY this context. If a company isn't mentioned, don't speculate about it. Cite which company/year each point comes from.

Context:
{context}

Question: {query}

Answer:"""

    for attempt in range(3):
        try:
            response = groq_client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except RateLimitError:
            print("Rate limited, waiting 10s...")
            time.sleep(10)

    return "Failed after retries."


if __name__ == "__main__":
    query = "Which companies mention antitrust or regulatory litigation?"
    print(scan_litigation(query))