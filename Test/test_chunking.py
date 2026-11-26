from app.services.text_chunker import chunk_text
def test_chunk_text_returns_chunks():

    text = """
    Invoice Number: INV-1001
    Vendor: ABC Technologies
    Invoice Amount: 15340
    """

    chunks = chunk_text(
        text=text,
        chunk_size=500,
        overlap=50
    )

    assert len(chunks) > 0
    
    
def test_chunk_text_preserves_invoice_information():

    text = """
    Invoice Number: INV-1001
    Vendor: ABC Technologies
    Invoice Amount: 15340
    """

    chunks = chunk_text(
        text=text,
        chunk_size=500,
        overlap=50
    )

    combined_text = " ".join(chunks)

    assert "INV-1001" in combined_text
    assert "ABC Technologies" in combined_text
    assert "15340" in combined_text
    
import pytest
def test_chunk_text_raises_error_for_empty_text():
    with pytest.raises(ValueError, match="Text cannot be empty."):
        chunk_text("")