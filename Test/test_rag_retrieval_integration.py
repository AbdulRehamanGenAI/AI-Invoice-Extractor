import os

import pytest
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture
def test_engine():
    database_url = os.getenv("TEST_DATABASE_URL")

    if not database_url:
        pytest.skip("TEST_DATABASE_URL is not configured.")

    engine = create_engine(database_url)

    yield engine

    engine.dispose()


def test_pgvector_retrieves_nearest_invoice(test_engine):

    # Create known test embeddings
    query_embedding = [1.0] + [0.0] * 767

    relevant_embedding = [0.99, 0.1] + [0.0] * 766

    irrelevant_embedding = [0.0, 1.0] + [0.0] * 766

    with test_engine.begin() as connection:

        # Insert test invoice chunks
        connection.execute(
            text("""
                INSERT INTO embedding_test
                    (content, embedding)
                VALUES
                    (:content1, CAST(:embedding1 AS vector)),
                    (:content2, CAST(:embedding2 AS vector))
            """),
            {
                "content1": "Invoice INV-1002 amount is 9440",
                "embedding1": str(relevant_embedding),

                "content2": "Unrelated invoice information",
                "embedding2": str(irrelevant_embedding),
            },
        )

        # Search using vector similarity
        result = connection.execute(
            text("""
                SELECT content
                FROM embedding_test
                ORDER BY embedding <=> CAST(:query_embedding AS vector)
                LIMIT 1
            """),
            {
                "query_embedding": str(query_embedding)
            },
        ).fetchone()

    # Verify the retrieved chunk
    assert result is not None

    assert "INV-1002" in result[0]

    assert "9440" in result[0]