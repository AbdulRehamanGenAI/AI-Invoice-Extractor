from app.services.reranker import rerank_documents


query = "What is the total payable amount for invoice INV-1005?"

documents = [
    {
        "invoice_id": 5,
        "chunk_text": "Vendor ABC Technologies. Outstanding payable amount INR 26432."
    },
    {
        "invoice_id": 6,
        "chunk_text": "Invoice INV-1006. Total amount INR 15000."
    },
    {
        "invoice_id": 5,
        "chunk_text": "Invoice INV-1005. Invoice date 28-Oct-2026."
    },
    {
        "invoice_id": 5,
        "chunk_text": "Invoice INV-1005. Total amount INR 26432."
    },
    {
        "invoice_id": 7,
        "chunk_text": "Payment terms Net 30 days."
    }
]


results = rerank_documents(
    query=query,
    documents=documents,
    top_k=3
)


print("\nReranked Results:\n")

for result in results:
    print("Invoice ID:", result["invoice_id"])
    print("Rerank Score:", result["rerank_score"])
    print("Text:", result["chunk_text"])
    print("-" * 60)