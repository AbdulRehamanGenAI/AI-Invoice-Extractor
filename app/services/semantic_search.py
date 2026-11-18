from sqlalchemy.orm import Session
from app.models.invoice import Invoice
from app.models.invoice_embedding import InvoiceEmbedding
from app.services.embedding_service import generate_embedding


def search_invoice_embeddings(
    db: Session,
    question: str,
    limit: int = 5,
    invoice_id: int | None = None,
    vendor_id: int | None = None
) -> list[dict]:

    # Step 1: Validate input
    if not question.strip():
        raise ValueError("Search question cannot be empty.")

    if limit <= 0:
        raise ValueError("Search limit must be greater than zero.")

    # Step 2: Convert question into an embedding
    query_embedding = generate_embedding(question)

    # Step 3: Prepare database query
    query = db.query(InvoiceEmbedding)

    # Step 4: Optionally filter by invoice ID
    if invoice_id is not None:
        query = query.filter(
            InvoiceEmbedding.invoice_id == invoice_id
        )

    if vendor_id is not None:
        query = query.join(
            Invoice,
            Invoice.id == InvoiceEmbedding.invoice_id
        ).filter(
            Invoice.vendor_id == vendor_id
        )

    # Step 5: Find the most similar chunks
    results = (
        query
        .order_by(
            InvoiceEmbedding.embedding.cosine_distance(query_embedding)
        )
        .limit(limit)
        .all()
    )

    # Step 6: Return matching chunks
    return [
        {
            "embedding_id": record.id,
            "invoice_id": record.invoice_id,
            "chunk_text": record.chunk_text,
        }
        for record in results
    ]