from app.services.db import get_collection, get_embed_model
from app.services.groq_service import get_groq_completion
from app.models import AskRequest, AskResponse, Source
import json

def ask_question(request: AskRequest) -> AskResponse:
    collection = get_collection()
    embed_model = get_embed_model()
    
    query_embedding = embed_model.encode(request.text).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5,
        where={"ticker": request.ticker.upper()}
    )
    
    retrieved_documents = results["documents"][0]
    retrieved_metadatas = results["metadatas"][0]
    
    if not retrieved_documents:
        return AskResponse(
            answer=f"No filing data found for {request.ticker.upper()} — try ingesting it first or checking the ticker.",
            ticker=request.ticker.upper(),
            sources=[]
        )

    context_pieces = []
    sources = []
    
    for i, (doc, meta) in enumerate(zip(retrieved_documents, retrieved_metadatas)):
        source = Source(
            ticker=meta["ticker"],
            fiscal_year=str(meta["fiscal_year"]),
            section=meta["section"],
            text=doc,
            source_url=None # We could generate sec.gov URLs here if we had accession numbers
        )
        sources.append(source)
        context_pieces.append(f"[Source {i+1}]: {doc}")

    context = "\n\n---\n\n".join(context_pieces)

    prompt = f"""You are a financial analyst assistant. Answer the question using ONLY the context below, which is excerpted from {request.ticker.upper()}'s SEC 10-K filing. 
If the context doesn't contain the answer, explicitly state that you cannot answer based on the provided filings.
Clearly distinguish what the filing says from any external inference. Do not use outside knowledge.
Cite your sources using the [Source N] labels.

Context:
{context}

Question: {request.text}

Answer:"""

    answer_text = get_groq_completion(prompt)
    
    return AskResponse(
        answer=answer_text,
        ticker=request.ticker.upper(),
        sources=sources
    )
