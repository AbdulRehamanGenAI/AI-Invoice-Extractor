from app.services.text_chunker import chunk_text

invoice_text = """
Invoice Number: INV-1002
Vendor: Bright Star Supplies
Invoice Date: 2026-10-28
Due Date: 2026-11-27
Subtotal: INR 8000
GST: INR 1440
Total Amount: INR 9440
Payment Status: Pending
"""

chunks = chunk_text(
    text=invoice_text,
    chunk_size=100,
    overlap=20
)

for index, chunk in enumerate(chunks, start=1):
    print(f"\nChunk {index}:")
    print(chunk)