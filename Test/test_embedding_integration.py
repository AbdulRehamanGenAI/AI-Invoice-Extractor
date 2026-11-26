import os
from unittest import result
import json
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

load_dotenv()

@pytest.fixture
def test_engine():
    """
    Create a database engine for integration testing.

    TEST_DATABASE_URL should point to a separate test database.
    """

    database_url = os.getenv("TEST_DATABASE_URL")

    if not database_url:
        pytest.skip("TEST_DATABASE_URL is not configured.")

    engine = create_engine(database_url)

    yield engine

    engine.dispose()


def test_database_connection(test_engine):
    """
    Verify that the application can connect to PostgreSQL.
    """

    with test_engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))

        assert result.scalar() == 1


def test_pgvector_extension_exists(test_engine):
    """
    Verify that the pgvector extension is available
    in the test database.
    """

    with test_engine.connect() as connection:
        result = connection.execute(
            text("""
                SELECT EXISTS (
                    SELECT 1
                    FROM pg_extension
                    WHERE extname = 'vector'
                )
            """))
        
        extension_exists = result.scalar()

        assert extension_exists is True
        
        
def test_postgres_can_store_and_retrieve_embedding(test_engine):
    embedding = [0.1] * 768

    with test_engine.begin() as connection:
        connection.execute(
            text("""
                INSERT INTO embedding_test (content, embedding)
                VALUES (:content, CAST(:embedding AS vector))
            """),
            {
                "content": "Invoice amount is 15340",
                "embedding": str(embedding),
            },
        )

        result = connection.execute(
            text("""
                SELECT content, embedding
                FROM embedding_test
                WHERE content = :content
                ORDER BY id DESC
                LIMIT 1
            """),
            {"content": "Invoice amount is 15340"},
        ).fetchone()

    assert result is not None
    assert result[0] == "Invoice amount is 15340"
    stored_embedding = json.loads(result[1])
    assert len(stored_embedding) == 768
    assert stored_embedding[0] == pytest.approx(0.1)