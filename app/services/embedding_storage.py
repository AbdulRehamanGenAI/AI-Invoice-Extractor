from sqlalchemy.orm import Session

from app.models.invoice_embedding import InvoiceEmbedding
from app.services.embedding_service import generate_embedding
from app.services.text_chunker import chunk_text


def store_invoice_embedding(
    db: Session,
    invoice_id: int,
    pages: list[dict]
) -> list[InvoiceEmbedding]:

    records = []
    chunk_index = 0

    try:
        for page in pages:

            page_number = page["page_number"]
            page_text = page["text"]

            chunks = chunk_text(
                text=page_text,
                chunk_size=500,
                overlap=50
            )

            for chunk in chunks:

                embedding_values = generate_embedding(chunk)

                record = InvoiceEmbedding(
                    invoice_id=invoice_id,
                    chunk_index=chunk_index,
                    page_number=page_number,
                    chunk_text=chunk,
                    embedding=embedding_values
                )

                db.add(record)
                records.append(record)

                chunk_index += 1

        db.commit()

        for record in records:
            db.refresh(record)

        return records

    except Exception:
        db.rollback()
        raise