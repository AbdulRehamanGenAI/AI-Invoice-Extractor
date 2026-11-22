
from app.db.session import SessionLocal
from app.services.hybrid_search import search_hybrid


db = SessionLocal()

try:
    query = "What is the total payable amount for invoice INV-1005?"

    results = search_hybrid(
        db=db,
        query=query,
        top_k=5
    )

    print("\nHybrid Search Results\n")

    for result in results:
        print("Invoice ID:", result["invoice_id"])
        print("Page:", result["page_number"])
        print("RRF Score:", result["rrf_score"])
        print("Text:", result["chunk_text"])
        print("-" * 60)

finally:
    db.close()