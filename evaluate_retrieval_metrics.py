from app.db.session import SessionLocal
from app.services.hybrid_search import search_hybrid
from golden_dataset import GOLDEN_DATASET


def get_invoice_number(document):
    """
    Extract invoice number from a retrieved document.
    """

    # If invoice_number is directly available
    if document.get("invoice_number"):
        return document["invoice_number"]

    # Otherwise, try to find it inside chunk_text
    chunk_text = document.get("chunk_text", "")

    import re

    match = re.search(r"INV-\d+", chunk_text)

    if match:
        return match.group(0)

    return None


def evaluate_retrieval(
    db,
    golden_dataset,
    top_k=5
):
    total_precision = 0
    total_recall = 0
    total_precision_at_k = 0
    total_recall_at_k = 0

    total_queries = len(golden_dataset)

    for item in golden_dataset:

        query = item["query"]

        relevant_invoices = set(
            item["relevant_invoices"]
        )

        print("\nQuery:", query)

        # Retrieve documents using hybrid search
        results = search_hybrid(
            db=db,
            query=query,
            top_k=top_k
        )

        # Extract invoice numbers from results
        retrieved_invoices = []

        for document in results:

            invoice_number = get_invoice_number(
                document
            )

            if invoice_number:
                retrieved_invoices.append(
                    invoice_number
                )

        # Remove duplicate invoices while
        # preserving their retrieval order
        retrieved_invoices = list(
            dict.fromkeys(retrieved_invoices)
        )

        # Relevant invoices retrieved
        relevant_retrieved = (
            set(retrieved_invoices)
            & relevant_invoices
        )

        relevant_count = len(
            relevant_retrieved
        )

        retrieved_count = len(
            retrieved_invoices
        )

        expected_count = len(
            relevant_invoices
        )

        # Overall Precision
        precision = (
            relevant_count / retrieved_count
            if retrieved_count > 0
            else 0
        )

        # Overall Recall
        recall = (
            relevant_count / expected_count
            if expected_count > 0
            else 0
        )

        # Precision@K
        precision_at_k = (
            relevant_count / top_k
        )

        # Recall@K
        recall_at_k = (
            relevant_count / expected_count
            if expected_count > 0
            else 0
        )

        total_precision += precision
        total_recall += recall
        total_precision_at_k += precision_at_k
        total_recall_at_k += recall_at_k

        print("Expected:", relevant_invoices)
        print("Retrieved:", retrieved_invoices)
        print("Relevant retrieved:", relevant_retrieved)

        print(f"Precision: {precision:.2f}")
        print(f"Recall: {recall:.2f}")
        print(f"Precision@{top_k}: {precision_at_k:.2f}")
        print(f"Recall@{top_k}: {recall_at_k:.2f}")

    # Average metrics across all queries
    if total_queries > 0:

        print("\n========== FINAL RESULTS ==========")

        print(
            "Average Precision:",
            round(total_precision / total_queries, 2)
        )

        print(
            "Average Recall:",
            round(total_recall / total_queries, 2)
        )

        print(
            f"Average Precision@{top_k}:",
            round(total_precision_at_k / total_queries, 2)
        )

        print(
            f"Average Recall@{top_k}:",
            round(total_recall_at_k / total_queries, 2)
        )


if __name__ == "__main__":

    db = SessionLocal()

    try:
        evaluate_retrieval(
            db=db,
            golden_dataset=GOLDEN_DATASET,
            top_k=5
        )

    finally:
        db.close()