from docx import Document

from app.services.docx_extractor import extract_text_from_docx

# Create a sample Word invoice
document = Document()

document.add_heading("TAX INVOICE", level=1)

document.add_paragraph("Invoice Number: DOCX-1001")
document.add_paragraph("Vendor: ABC Technologies Pvt Ltd")
document.add_paragraph("Invoice Date: 18-Nov-2026")

# Create invoice items table
table = document.add_table(rows=1, cols=3)

table.rows[0].cells[0].text = "Item"
table.rows[0].cells[1].text = "Quantity"
table.rows[0].cells[2].text = "Amount"

row = table.add_row().cells
row[0].text = "Laptop"
row[1].text = "2"
row[2].text = "50000"

document.add_paragraph("Total Amount: INR 50000")

document.save("sample_invoice.docx")

# Read the generated DOCX file
with open("sample_invoice.docx", "rb") as file:
    file_bytes = file.read()

# Extract text
extracted_text = extract_text_from_docx(file_bytes)

print("Extracted DOCX Content:")
print(extracted_text)