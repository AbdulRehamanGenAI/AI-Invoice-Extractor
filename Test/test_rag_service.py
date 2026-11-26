import pytest

from app.services.rag_service import answer_invoice_question

def test_answer_invoice_question_rejects_empty_question():
    with pytest.raises(ValueError, match="Question cannot be empty."):
        answer_invoice_question(
            db=None,
            question=""
        )