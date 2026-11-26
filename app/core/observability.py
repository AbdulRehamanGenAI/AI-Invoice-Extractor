from dotenv import load_dotenv

# Load environment variables before initializing SDK clients
load_dotenv()

from langfuse import get_client, observe
from langsmith import traceable

from app.core.logger import logger


# =========================================================
# LANGFUSE CLIENT
# =========================================================

langfuse = get_client()


# =========================================================
# LANGSMITH INPUT / OUTPUT REDACTION
# =========================================================

def hide_trace_inputs(inputs: dict) -> dict:
    """
    Hide function inputs from LangSmith.

    Invoice questions and retrieved context may contain
    confidential financial information.
    """

    return {
        "redacted": True
    }


def hide_trace_outputs(outputs) -> dict:
    """
    Hide function outputs from LangSmith.
    """

    return {
        "redacted": True
    }


# =========================================================
# RAG PIPELINE DECORATOR
# =========================================================

def trace_rag_pipeline(func):
    """
    Trace the complete RAG pipeline in both platforms.
    """

    # LangSmith decorator
    func = traceable(
        name="invoice-rag-pipeline",
        run_type="chain",
        tags=["invoice-rag", "rag-pipeline"],
        metadata={
            "project": "AI-Invoice-Extractor"
        },
        process_inputs=hide_trace_inputs,
        process_outputs=hide_trace_outputs
    )(func)

    # Langfuse decorator
    func = observe(
        name="invoice-rag-pipeline",
        capture_input=True,
        capture_output=True
    )(func)

    return func


# =========================================================
# RETRIEVAL DECORATOR
# =========================================================

def trace_retrieval(func):
    """
    Trace the document retrieval stage.
    """

    func = traceable(
        name="invoice-retrieval",
        run_type="retriever",
        tags=["invoice-rag", "retrieval"],
        process_inputs=hide_trace_inputs,
        process_outputs=hide_trace_outputs
    )(func)

    func = observe(
        name="invoice-retrieval",
        as_type="retriever",
        capture_input=True,
        capture_output=True
    )(func)

    return func


# =========================================================
# GEMINI GENERATION DECORATOR
# =========================================================

def trace_gemini_generation(func):
    """
    Trace Gemini answer generation.
    """

    func = traceable(
        name="gemini-invoice-generation",
        run_type="llm",
        tags=["gemini", "invoice-generation"],
        metadata={
            "provider": "Google Gemini"
        },
        process_inputs=hide_trace_inputs,
        process_outputs=hide_trace_outputs
    )(func)

    func = observe(
        name="gemini-invoice-generation",
        as_type="generation",
        capture_input=False,
        capture_output=False
    )(func)

    return func


# =========================================================
# LANGFUSE SAFE METADATA UPDATE
# =========================================================

def update_generation_metadata(
    query: str,
    context: str,
    answer: str,
    model_name: str
):
    """
    Send only safe metadata to Langfuse.

    Do not send invoice context or the full answer here.
    """

    try:
        langfuse.update_current_generation(
            model=model_name,
            input={
                "query_length": len(query),
                "context_length": len(context)
            },
            output={
                "answer_length": len(answer)
            },
            metadata={
                "provider": "Google Gemini",
                "application": "AI-Invoice-Extractor"
            }
        )

    except Exception as error:
        logger.warning(
            "Unable to update Langfuse generation metadata: %s",
            type(error).__name__
        )


# =========================================================
# FLUSH EVENTS
# =========================================================

def flush_observability():
    """
    Flush pending Langfuse events.

    Useful for short-lived scripts and tests.
    """

    try:
        langfuse.flush()

    except Exception as error:
        logger.warning(
            "Langfuse flush failed: %s",
            type(error).__name__
        )