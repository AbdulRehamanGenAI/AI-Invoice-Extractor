from app.db.session import SessionLocal

from app.models.vendor import Vendor
from app.models.invoice import Invoice
from app.models.payment import Payment
from app.models.invoice_embedding import InvoiceEmbedding

from app.services.semantic_search import search_invoice_embeddings


db = SessionLocal()

try:
    results = search_invoice_embeddings(
        db=db,
        question="What is the total invoice amount?",
        vendor_id=1
    )

    print("\nSearch Results:")

    for result in results:
        print("-----------------------------")
        print("Invoice ID:", result["invoice_id"])
        print("Embedding ID:", result["embedding_id"])
        print("Text:", result["chunk_text"])

finally:
    db.close()