import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import chromadb
from groq import Groq

load_dotenv()

app = FastAPI()

embed_model = SentenceTransformer("all-MiniLM-L6-v2")
db_client = chromadb.PersistentClient(path="./chroma_db")
collection = db_client.get_or_create_collection(name="filings")
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class Question(BaseModel):
    text: str

@app.post("/ask")
def ask(question: Question):
    query_embedding = embed_model.encode(question.text).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=3)
    retrieved_chunks = results["documents"][0]
    context = "\n\n---\n\n".join(retrieved_chunks)

    prompt = f"""You are a financial analyst assistant. Answer the question using ONLY the context below, which is excerpted from an SEC 10-K filing. If the context doesn't contain the answer, say so.

Context:
{context}

Question: {question.text}

Answer:"""

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}]
    )

    return {"answer": response.choices[0].message.content}