from app.services.semantic_chunker import semantic_chunk_text

invoice_text = """
Invoice Number: INV-1004
Vendor: Bright Star Supplies Pvt. Ltd.

Computer accessories bundle: INR 5000
USB-C docking station: INR 6000

Subtotal: INR 11000
GST: INR 1980
Total Amount: INR 12980

Payment Terms: 30 days
"""

chunks = semantic_chunk_text(
    text=invoice_text,
    chunk_size=500,
    similarity_threshold=0.65
)

for index, chunk in enumerate(chunks, start=1):

    print(f"\nSemantic Chunk {index}:")
    print(chunk)