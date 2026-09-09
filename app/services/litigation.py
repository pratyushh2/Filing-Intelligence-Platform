from app.services.db import get_collection, get_embed_model
from app.services.groq_service import get_groq_completion
from app.models import LitigationRequest, LitigationResponse, LitigationMatch

def scan_litigation(request: LitigationRequest) -> LitigationResponse:
    collection = get_collection()
    embed_model = get_embed_model()
    
    query_embedding = embed_model.encode(request.query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=8,
        where={"section": "Item 3"}
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    if not documents:
        return LitigationResponse(
            answer="No litigation-related disclosures found matching that query in the available filings.",
            matches=[]
        )

    context_pieces = []
    matches = []
    for doc, meta in zip(documents, metadatas):
        label = f"[{meta['ticker']} - {meta['fiscal_year']}]"
        context_pieces.append(f"{label}\n{doc}")
        
        matches.append(LitigationMatch(
            ticker=meta['ticker'],
            fiscal_year=str(meta['fiscal_year']),
            section=meta['section'],
            text=doc
        ))

    context = "\n\n---\n\n".join(context_pieces)

    prompt = f"""You are a financial analyst assistant. Below are excerpts from Legal Proceedings (Item 3) sections of various companies' 10-K filings, each labeled with the company ticker and fiscal year. 
Answer the question using ONLY this context. 
If a company isn't mentioned, don't speculate about it. 
Do not claim that a company has litigation unless the retrieved Item 3 context supports it.
If no relevant companies are found for the query in the context, explicitly say so.
Cite which company/year each point comes from.

Context:
{context}

Question: {request.query}

Answer:"""

    answer_text = get_groq_completion(prompt)

    return LitigationResponse(
        answer=answer_text,
        matches=matches
    )
