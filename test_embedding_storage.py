from app.db.session import SessionLocal

from app.models.invoice import Invoice
from app.models.vendor import Vendor
from app.models.payment import Payment
from app.models.invoice_embedding import InvoiceEmbedding

from app.services.invoice_extractor import extract_pages_from_pdf
from app.services.embedding_storage import store_invoice_embedding


db = SessionLocal()

try:
    invoice_id = 4

    pdf_path = r"C:\Users\HAI\Downloads\sample_invoice_1004.pdf"

    with open(pdf_path, "rb") as file:
        file_bytes = file.read()

    # Extract text page by page
    pages = extract_pages_from_pdf(file_bytes)

    # Generate and store embeddings with metadata
    records = store_invoice_embedding(
        db=db,
        invoice_id=invoice_id,
        pages=pages
    )

    print("\nStored Embedding Records:")

    for record in records:
        print("-------------------------")
        print("Embedding ID:", record.id)
        print("Invoice ID:", record.invoice_id)
        print("Chunk Index:", record.chunk_index)
        print("Page Number:", record.page_number)
        print("Chunk Text:", record.chunk_text)

finally:
    db.close()