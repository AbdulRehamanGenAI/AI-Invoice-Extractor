from app.services.invoice_extractor import extract_pages_from_pdf
import pymupdf


pdf_path = r"C:\Users\HAI\Downloads\sample_invoice_1004.pdf"

with open(pdf_path, "rb") as file:
    file_bytes = file.read()

pages = extract_pages_from_pdf(file_bytes)

print("Total pages:", len(pages))

for page in pages:
    print("-------------------------")
    print("Page Number:", page["page_number"])
    print("Extracted Text:")
    print(page["text"])