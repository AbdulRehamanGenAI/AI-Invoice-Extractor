import os

from dotenv import load_dotenv
from google import genai

load_dotenv()


def generate_embedding(text: str) -> list[float]:
    if not text.strip():
        raise ValueError("Text cannot be empty.")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing from .env")

    client = genai.Client(api_key=api_key)

    response = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config={"output_dimensionality": 768},
    )

    if not response.embeddings:
        raise ValueError("No embedding returned.")

    return response.embeddings[0].values