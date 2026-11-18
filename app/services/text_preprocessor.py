import re


def preprocess_text(text: str) -> str:

    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")

    # Step 1: Remove unnecessary spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Step 2: Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Step 3: Remove spaces at the beginning and end of lines
    text = "\n".join(
        line.strip() for line in text.splitlines()
    )

    # Step 4: Remove unnecessary spaces around text
    text = text.strip()

    return text