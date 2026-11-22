import json
from google import genai
from google.genai import types

from app.core.logger import logger


client = genai.Client()


def evaluate_metric(
    metric_name: str,
    query: str,
    answer: str,
    context: str,
    reference_answer: str = ""
):
    """
    Evaluate one RAG quality metric using Gemini.
    """

    prompt = f"""
You are evaluating the quality of a RAG-based invoice assistant.

Metric: {metric_name}

User Question:
{query}

Generated Answer:
{answer}

Retrieved Context:
{context}

Reference Answer:
{reference_answer}

Evaluate the response according to the following metric:

Correctness:
Compare the generated answer with the reference answer.
Check whether the answer is factually correct and answers the question.

Faithfulness:
Check whether the generated answer is supported by the retrieved context.
Penalize unsupported claims or information invented by the model.

Context Relevance:
Check whether the retrieved context is relevant to answering the user's question.
Irrelevant invoice information should receive a lower score.

Return a score between 0 and 1.

0 means completely poor.
1 means excellent.

Return ONLY valid JSON in this format:

{{
    "score": 0.0,
    "reason": "Brief explanation of the score"
}}
"""

    logger.info("Starting RAG evaluation: %s", metric_name)

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json"
        )
    )

    result = json.loads(response.text)

    logger.info(
        "RAG evaluation completed: %s | Score: %.2f",
        metric_name,
        result["score"]
    )

    return result