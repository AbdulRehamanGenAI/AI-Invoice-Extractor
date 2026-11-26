import json
from google import genai
from google.genai import types

from app.core.logger import logger

#client = genai.Client()
client = genai.Client(
    http_options=types.HttpOptions(
        timeout=60000
    )
)


METRIC_INSTRUCTIONS = {
    "Correctness": """
Compare the generated answer with the reference answer.
Check whether the answer is factually correct and answers the question.
""",
    "Faithfulness": """
Check whether the generated answer is supported by the retrieved context.
Penalize unsupported claims or information invented by the model.
""",
    "Context Relevance": """
Check whether the retrieved context is relevant to answering the question.
Irrelevant invoice information should receive a lower score.
""",
}


def evaluate_metric(
    metric_name: str, query: str, answer: str, context: str, reference_answer: str = ""
):
    """
    Evaluate one RAG quality metric using Gemini.
    """

    if metric_name not in METRIC_INSTRUCTIONS:
        raise ValueError(f"Unsupported metric: {metric_name}")

    if metric_name == "Correctness" and not reference_answer:
        raise ValueError("Reference answer is required for Correctness evaluation")
    metric_instruction = METRIC_INSTRUCTIONS[metric_name]

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

Evaluation Instructions:
{metric_instruction}

Rules:
- Use only the provided evidence.
- Do not assume the generated answer is correct.
- If evidence is insufficient, explain that.
- Return a score between 0 and 1.
- 0 means completely poor.
- 1 means excellent.

Return ONLY valid JSON:

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
            response_mime_type="application/json")
    )
    
    logger.info("Gemini evaluation response received")
    if not response.text:
        raise ValueError("Gemini returned an empty evaluation response")

    result = json.loads(response.text)

    score = float(result["score"])

    if not 0.0 <= score <= 1.0:
        raise ValueError(f"Invalid evaluation score: {score}")

    result["score"] = score

    logger.info("RAG evaluation completed: %s | Score: %.2f", metric_name, score)

    return result
