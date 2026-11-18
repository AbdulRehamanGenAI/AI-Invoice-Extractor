import fitz

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from a PDF invoice.
    """
    if not file_bytes:
        raise ValueError("The uploaded PDF is empty.")

    try:
        with fitz.open(stream=file_bytes, filetype="pdf") as document:
            if document.page_count == 0:
                raise ValueError("The PDF contains no pages.")

            extracted_text = ""

            for page in document:
                extracted_text += page.get_text() + "\n"

    except Exception as error:
        raise ValueError(
            f"Unable to read the PDF: {error}"
        ) from error

    if not extracted_text.strip():
        raise ValueError(
            "No text found in PDF. It may be blank or scanned."
        )

    return extracted_text.strip()

import pymupdf

def extract_pages_from_pdf(file_bytes: bytes) -> list[dict]:

    if not file_bytes:
        raise ValueError("The uploaded PDF is empty.")

    pages = []

    try:
        with pymupdf.open(
            stream=file_bytes,
            filetype="pdf"
        ) as document:

            if document.page_count == 0:
                raise ValueError("The PDF contains no pages.")

            for page_number, page in enumerate(document, start=1):

                page_text = page.get_text().strip()

                if page_text:
                    pages.append({
                        "page_number": page_number,
                        "text": page_text
                    })

    except Exception as error:
        raise ValueError(
            f"Unable to read the PDF: {error}"
        ) from error

    if not pages:
        raise ValueError(
            "No text found in PDF. It may be blank or scanned."
        )

    return pages