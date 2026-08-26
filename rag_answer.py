import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import chromadb
from groq import Groq

load_dotenv()

embed_model = SentenceTransformer("all-MiniLM-L6-v2")
db_client = chromadb.PersistentClient(path="./chroma_db")
collection = db_client.get_or_create_collection(name="filings")
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask(question, ticker, n_results=3):
    query_embedding = embed_model.encode(question).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where={"ticker": ticker.upper()}
    )
    retrieved_chunks = results["documents"][0]

    if not retrieved_chunks:
        return f"No filing data found for {ticker.upper()} — try ingesting it first."

    context = "\n\n---\n\n".join(retrieved_chunks)

    prompt = f"""You are a financial analyst assistant. Answer the question using ONLY the context below, which is excerpted from {ticker.upper()}'s SEC 10-K filing. If the context doesn't contain the answer, say so.

Context:
{context}

Question: {question}

Answer:"""

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    answer = ask("What are the main competitive risks?", "TSLA")
    print(answer)