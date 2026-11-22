from app.services.rag_evaluation import evaluate_metric


def test_rag_evaluation():

    query = "What is the amount of invoice INV-1001?"

    answer = "The invoice amount is ₹15,340."

    reference_answer = "The invoice amount is ₹15,340."

    context = """
    Invoice Number: INV-1001
    Vendor: ABC Technologies Pvt. Ltd.
    Invoice Amount: ₹15,340
    Currency: INR
    """

    # 1. Correctness
    correctness = evaluate_metric(
        metric_name="Correctness",
        query=query,
        answer=answer,
        context=context,
        reference_answer=reference_answer
    )

    # 2. Faithfulness
    faithfulness = evaluate_metric(
        metric_name="Faithfulness",
        query=query,
        answer=answer,
        context=context
    )

    # 3. Context Relevance
    context_relevance = evaluate_metric(
        metric_name="Context Relevance",
        query=query,
        answer=answer,
        context=context
    )

    print("\nRAG Evaluation Results")

    print("Correctness:", correctness)
    print("Faithfulness:", faithfulness)
    print("Context Relevance:", context_relevance)

if __name__ == "__main__":
    test_rag_evaluation()