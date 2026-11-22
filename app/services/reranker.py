from sentence_transformers import CrossEncoder


# Load the model once when the module is imported
reranker_model = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


def rerank_documents(
    query: str,
    documents: list[dict],
    top_k: int = 5
):
    if not documents:
        return []

    # Create query-document pairs
    pairs = [
        (query, document["chunk_text"])
        for document in documents
    ]

    # Calculate relevance scores
    scores = reranker_model.predict(pairs)

    # Add reranking score to each document
    for document, score in zip(documents, scores):
        document["rerank_score"] = float(score)

    # Sort documents by relevance score
    reranked_documents = sorted(
        documents,
        key=lambda document: document["rerank_score"],
        reverse=True
    )

    # Return the top relevant documents
    return reranked_documents[:top_k]