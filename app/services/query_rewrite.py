from google import genai
from app.core.config import GEMINI_API_KEY


client = genai.Client(
    api_key=GEMINI_API_KEY
)

def rewrite_query(query: str) -> str:

    prompt = f"""
You are a query rewriting assistant for an invoice
document retrieval system.

Rewrite the user's question into a clear and specific
search query suitable for BM25 and vector search.

Rules:
- Preserve invoice numbers and vendor names.
- Do not answer the question.
- Do not invent missing information.
- Keep the rewritten query concise.
- Return only the rewritten query.

User question:
{query}
"""

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
    )

    rewritten_query = response.text.strip()

    return rewritten_query