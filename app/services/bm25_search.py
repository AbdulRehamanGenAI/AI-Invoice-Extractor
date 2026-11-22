from rank_bm25 import BM25Okapi
from sqlalchemy.orm import Session

from app.models.invoice_embedding import InvoiceEmbedding

def search_bm25(
    db: Session,
    query: str,
    top_k: int = 5,
    invoice_id: int | None = None
):
    # 1. Fetch invoice chunks from PostgreSQL
    query_db = db.query(InvoiceEmbedding)

    # 2. Optional invoice-specific filtering
    if invoice_id is not None:
        query_db = query_db.filter(
            InvoiceEmbedding.invoice_id == invoice_id
        )

    chunks = query_db.all()

    if not chunks:
        return []

    # 3. Prepare text documents for BM25
    documents = [
        chunk.chunk_text.lower().split()
        for chunk in chunks
    ]

    # 4. Create BM25 index
    bm25 = BM25Okapi(documents)

    # 5. Tokenize the user's question
    tokenized_query = query.lower().split()

    # 6. Calculate BM25 scores
    scores = bm25.get_scores(tokenized_query)

    # 7. Rank chunks by score
    ranked_results = sorted(
        zip(chunks, scores),
        key=lambda item: item[1],
        reverse=True
    )

    # 8. Return top matching chunks
    results = []

    for chunk, score in ranked_results[:top_k]:
        if score > 0:
            results.append({
                "embedding_id": chunk.id,
                "invoice_id": chunk.invoice_id,
                "chunk_index": chunk.chunk_index,
                "page_number": chunk.page_number,
                "chunk_text": chunk.chunk_text,
                "bm25_score": float(score)
            })

    return results