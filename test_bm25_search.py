from app.db.session import SessionLocal
from app.services.bm25_search import search_bm25


db = SessionLocal()

try:
    query = "INV-1005 total amount"

    results = search_bm25(
        db=db,
        query=query,
        top_k=5
    )

    print(f"\nBM25 Search Query: {query}\n")

    for result in results:
        print("Invoice ID:", result["invoice_id"])
        print("Page:", result["page_number"])
        print("BM25 Score:", result["bm25_score"])
        print("Text:", result["chunk_text"])
        print("-" * 50)

finally:
    db.close()