from unittest.mock import patch, MagicMock

import pytest

from app.services.embedding_service import generate_embedding


@patch("app.services.embedding_service.genai.Client")
def test_generate_embedding_returns_vector(mock_client_class):
    # Arrange: create a fake Gemini response
    mock_response = MagicMock()
    mock_response.embeddings = [
        MagicMock(values=[0.1, 0.2, 0.3])
    ]

    # Mock Gemini client and API response
    mock_client = mock_client_class.return_value
    mock_client.models.embed_content.return_value = mock_response

    # Act: call our actual function
    result = generate_embedding("Invoice amount is 15340")

    # Assert: verify the returned embedding
    assert result == [0.1, 0.2, 0.3]

    # Verify Gemini was called with correct parameters
    mock_client.models.embed_content.assert_called_once_with(
        model="gemini-embedding-001",
        contents="Invoice amount is 15340",
        config={"output_dimensionality": 768},
    )
    
def test_generate_embedding_raises_error_for_empty_text():
    with pytest.raises(ValueError, match="Text cannot be empty."):
        generate_embedding("")
        
@patch.dict("os.environ", {}, clear=True)
def test_generate_embedding_raises_error_when_api_key_missing():
    with pytest.raises(
        ValueError,
        match="GEMINI_API_KEY is missing from .env"
    ):
        generate_embedding("Invoice amount is 15340")
        
        

@patch("app.services.embedding_service.genai.Client")
def test_generate_embedding_raises_error_when_no_embeddings(mock_client_class):
    # Arrange: mock Gemini response with no embeddings
    mock_response = MagicMock()
    mock_response.embeddings = []

    mock_client = mock_client_class.return_value
    mock_client.models.embed_content.return_value = mock_response

    # Act & Assert
    with pytest.raises(ValueError, match="No embedding returned."):
        generate_embedding("Invoice amount is 15340")
        
    
@patch("app.services.embedding_service.genai.Client")
def test_generate_embedding_handles_gemini_api_error(mock_client_class):
    mock_client = mock_client_class.return_value

    mock_client.models.embed_content.side_effect = Exception(
        "Gemini API error"
    )

    with pytest.raises(Exception, match="Gemini API error"):
        generate_embedding("Invoice amount is 15340")