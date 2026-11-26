from app.services.rag_evaluation import evaluate_metric

GOLDEN_DATASET = [
    {
        "query": "Find invoices from ABC Technologies",
        "relevant_invoices": ["INV-1001", "INV-1005", "INV-1008"],
        "reference_answer": "The relevant invoices are INV-1001, INV-1005, and INV-1008."
    },
    {
        "query": "Find invoice INV-1005",
        "relevant_invoices": ["INV-1005"],
        "reference_answer": "The invoice found is INV-1005."
    },
    {
        "query": "Find invoice from Bright Star Supplies",
        "relevant_invoices": ["INV-1002"],
        "reference_answer": "The invoice found is INV-1002."
    },
]


def test_rag_evaluation():

    for test_case in GOLDEN_DATASET:

        query = test_case["query"]
        reference_answer = test_case["reference_answer"]

        # Temporary answer and context for testing the evaluator
        answer = reference_answer
        context = reference_answer

        print(f"\nQuestion: {query}")

        correctness = evaluate_metric(
            metric_name="Correctness",
            query=query,
            answer=answer,
            context=context,
            reference_answer=reference_answer
        )

        faithfulness = evaluate_metric(
            metric_name="Faithfulness",
            query=query,
            answer=answer,
            context=context
        )

        context_relevance = evaluate_metric(
            metric_name="Context Relevance",
            query=query,
            answer=answer,
            context=context
        )

        print("Correctness:", correctness)
        print("Faithfulness:", faithfulness)
        print("Context Relevance:", context_relevance)


if __name__ == "__main__":
    test_rag_evaluation()