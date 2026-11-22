
from sqlalchemy.orm import Session
from app.core.logger import logger
from app.services.bm25_search import search_bm25
from app.services.embedding_service import generate_embedding
from app.models.invoice_embedding import InvoiceEmbedding


def search_hybrid(
    db: Session,
    query: str,
    top_k: int = 5,
    invoice_id: int | None = None,
    rrf_k: int = 60
):
    logger.info("Hybrid search started")
    # 1. BM25 keyword search
    bm25_results = search_bm25(
        db=db,
        query=query,
        top_k=20,
        invoice_id=invoice_id
    )

    # 2. Generate query embedding
    query_embedding = generate_embedding(query)

    # 3. Vector similarity search
    vector_query = db.query(InvoiceEmbedding)

    if invoice_id is not None:
        vector_query = vector_query.filter(
            InvoiceEmbedding.invoice_id == invoice_id
        )

    vector_results = (
        vector_query
        .order_by(
            InvoiceEmbedding.embedding.cosine_distance(
                query_embedding
            )
        )
        .limit(20)
        .all()
    )

    # 4. Store RRF scores
    fused_scores = {}

    # 5. Add BM25 ranking
    for rank, result in enumerate(bm25_results, start=1):
        chunk_id = result["embedding_id"]

        fused_scores[chunk_id] = (
            fused_scores.get(chunk_id, 0)
            + 1 / (rrf_k + rank)
        )

    # 6. Add vector ranking
    for rank, chunk in enumerate(vector_results, start=1):
        chunk_id = chunk.id

        fused_scores[chunk_id] = (
            fused_scores.get(chunk_id, 0)
            + 1 / (rrf_k + rank)
        )

    # 7. Sort by combined RRF score
    ranked_ids = sorted(
        fused_scores,
        key=fused_scores.get,
        reverse=True
    )

    # 8. Fetch final chunks
    final_chunks = (
        db.query(InvoiceEmbedding)
        .filter(InvoiceEmbedding.id.in_(ranked_ids))
        .all()
    )

    chunks_by_id = {
        chunk.id: chunk
        for chunk in final_chunks
    }

    # 9. Return ranked hybrid results
    results = []

    for chunk_id in ranked_ids[:top_k]:
        chunk = chunks_by_id.get(chunk_id)

        if chunk is None:
            continue

        results.append({
            "embedding_id": chunk.id,
            "invoice_id": chunk.invoice_id,
            "page_number": chunk.page_number,
            "chunk_text": chunk.chunk_text,
            "rrf_score": fused_scores[chunk_id]
        })
    logger.info(
    "Hybrid search completed. Retrieved %d results",
    len(results)
)

    return results