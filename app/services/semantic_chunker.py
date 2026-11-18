import re
import math

from app.services.embedding_service import generate_embedding


def cosine_similarity(vector1: list[float], vector2: list[float]) -> float:

    dot_product = sum(a * b for a, b in zip(vector1, vector2))

    magnitude1 = math.sqrt(sum(a * a for a in vector1))
    magnitude2 = math.sqrt(sum(b * b for b in vector2))

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    return dot_product / (magnitude1 * magnitude2)


def semantic_chunk_text(
    text: str,
    chunk_size: int = 500,
    similarity_threshold: float = 0.65
) -> list[str]:

    if not text.strip():
        raise ValueError("Text cannot be empty.")

    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive.")

    if not -1 <= similarity_threshold <= 1:
        raise ValueError("Similarity threshold must be between -1 and 1.")

    # Step 1: Split text into sentences and lines
    segments = re.split(r'(?<=[.!?])\s+|\n+', text.strip())

    segments = [
        segment.strip()
        for segment in segments
        if segment.strip()
    ]

    if not segments:
        return []

    # Step 2: Generate embeddings for each segment
    embeddings = [
        generate_embedding(segment)
        for segment in segments
    ]

    chunks = []
    current_chunk = segments[0]

    # Step 3: Compare neighbouring segments
    for index in range(1, len(segments)):

        similarity = cosine_similarity(
            embeddings[index - 1],
            embeddings[index]
        )

        segment = segments[index]

        # Step 4: Check semantic similarity and chunk size
        if (
            similarity >= similarity_threshold
            and len(current_chunk) + len(segment) + 1 <= chunk_size
        ):
            current_chunk += " " + segment

        else:
            chunks.append(current_chunk)

            current_chunk = segment

    # Step 5: Store the final chunk
    if current_chunk:
        chunks.append(current_chunk)

    return chunks