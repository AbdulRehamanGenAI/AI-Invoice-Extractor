from app.db.session import SessionLocal

from app.models.vendor import Vendor
from app.models.invoice import Invoice
from app.models.payment import Payment
from app.models.invoice_embedding import InvoiceEmbedding

from app.services.rag_service import answer_invoice_question


db = SessionLocal()

try:
    question = "What is the total amount of INV-1002?"

    result = answer_invoice_question(
        db=db,
        question=question
    )

    print("\nQuestion:", result["question"])
    print("\nAnswer:", result["answer"])

    print("\nSources:")

    for source in result["sources"]:
        print(
            f"Invoice ID: {source['invoice_id']} | "
            f"Embedding ID: {source['embedding_id']}"
        )
        print("Text:", source["chunk_text"])

finally:
    db.close()