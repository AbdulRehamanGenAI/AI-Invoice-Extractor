from docx import Document
from io import BytesIO


def extract_text_from_docx(file_bytes: bytes) -> str:

    if not file_bytes:
        raise ValueError("The uploaded DOCX file is empty.")

    try:
        document = Document(BytesIO(file_bytes))

        extracted_text = []

        # Extract paragraphs
        for paragraph in document.paragraphs:
            text = paragraph.text.strip()

            if text:
                extracted_text.append(text)

        # Extract tables
        for table in document.tables:
            for row in table.rows:
                row_text = [
                    cell.text.strip()
                    for cell in row.cells
                ]

                extracted_text.append(" | ".join(row_text))

    except Exception as error:
        raise ValueError(
            f"Unable to read the DOCX file: {error}"
        ) from error

    if not extracted_text:
        raise ValueError("No text found in DOCX file.")

    return "\n".join(extracted_text)