"""
TEXT CHUNKING TECHNIQUES

1. Character-Based Chunking:
   - Splits text based on a fixed number of characters.
   - Example: chunk_size = 500 means approximately 500 characters per chunk.
   - Limitation: Can break sentences and meaningful information.

2. Sentence-Aware Chunking:
   - Splits text based on sentence endings and line breaks.
   - Tries to keep complete sentences and invoice fields together.
   - Helps preserve meaningful text boundaries.

3. Semantic Chunking:
   - Groups text based on meaning and context.
   - Uses embeddings and semantic similarity to identify related content.
   - Keeps related information together even when sentence boundaries differ.
   - Not implemented yet; planned as a future improvement.

CHUNK SIZE:
   - Controls the maximum target size of each chunk.

CHUNK OVERLAP:
   - Repeats a portion of the previous chunk in the next chunk.
   - Helps preserve context between neighbouring chunks.
"""


import re

def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50
) -> list[str]:

    if not text.strip():
        raise ValueError("Text cannot be empty.")

    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("Overlap must be smaller than chunk size.")

    # Step 1: Split text into sentences or lines
    sentences = re.split(r'(?<=[.!?])\s+|\n+', text.strip())

    chunks = []
    current_chunk = ""

    # Step 2: Process each sentence
    for sentence in sentences:

        sentence = sentence.strip()

        if not sentence:
            continue

        # Step 3: Handle sentences longer than chunk_size
        if len(sentence) > chunk_size:
            words = sentence.split()
            for word in words:
                if current_chunk and len(current_chunk) + len(word) + 1 > chunk_size:
                    chunks.append(current_chunk)
                    current_chunk = ""

                current_chunk = (
                    current_chunk + " " + word
                ).strip()

            continue

        # Step 4: Check whether sentence fits
        if current_chunk and len(current_chunk) + len(sentence) + 1 > chunk_size:

            chunks.append(current_chunk)

            # Keep previous content for overlap
            previous_words = current_chunk.split()
            overlap_text = ""

            for word in reversed(previous_words):
                candidate = (word + " " + overlap_text).strip()

                if len(candidate) > overlap:
                    break

                overlap_text = candidate

            current_chunk = overlap_text

        # Step 5: Add sentence to current chunk
        current_chunk = (
            current_chunk + " " + sentence
        ).strip()

    # Step 6: Store remaining text
    if current_chunk:
        chunks.append(current_chunk)

    return chunks