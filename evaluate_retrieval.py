from golden_dataset import GOLDEN_DATASET
from app.core.logger import logger

logger.info("Evaluation Retrieval started")


def evaluate_retrieval(
    retrieve_function,
    golden_dataset,
    top_k=5,
    db=None
):
    total_queries = len(golden_dataset)

    hits = 0
    reciprocal_rank_sum = 0

    for test_case in golden_dataset:

        query = test_case["query"]
        expected_invoice = test_case["expected_invoice"]

        print("\n" + "=" * 60)
        print("Query:", query)
        print("Expected Invoice:", expected_invoice)

        # Retrieve top K documents
        results = retrieve_function(
            db,
            query,
            top_k=top_k
        )
        logger.info(
    "Hybrid search completed. Retrieved %d chunks",
    len(results)
)

        found_rank = None

        for rank, document in enumerate(results, start=1):

            chunk_text = document.get(
                "chunk_text", ""
            )

            # Check if the expected invoice number
            # appears in the retrieved chunk
            if expected_invoice.lower() in chunk_text.lower():

                found_rank = rank
                break

        if found_rank is not None:

            hits += 1

            reciprocal_rank_sum += (
                1 / found_rank
            )

            print(
                f"Correct invoice found at rank {found_rank}"
            )

        else:

            print(
                "Correct invoice NOT found in top results"
            )

    hit_rate = hits / total_queries

    mrr = (
        reciprocal_rank_sum / total_queries
    )

    print("\n" + "=" * 60)
    print("RETRIEVAL EVALUATION RESULTS")
    print("=" * 60)

    print(f"Total Queries: {total_queries}")
    print(f"Correctly Retrieved: {hits}")
    print(f"Hit@{top_k}: {hit_rate:.2f}")
    print(f"Recall@{top_k}: {hit_rate:.2f}")
    print(f"MRR: {mrr:.2f}")


if __name__ == "__main__":

    # Connect your existing retrieval function here
    from app.db.session import SessionLocal
    from app.services.hybrid_search import search_hybrid
    #from golden_dataset import GOLDEN_DATASET

    db = SessionLocal()
    try:
        evaluate_retrieval(
            retrieve_function=search_hybrid,
            golden_dataset=GOLDEN_DATASET,
            top_k=5,
            db=db
        )

    finally:
        db.close()