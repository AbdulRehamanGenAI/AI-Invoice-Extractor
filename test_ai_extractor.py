from app.services.ai_invoice_extractor import extract_invoice_fields

sample_text = """
Invoice Number: INV-1001
Vendor: ABC Technologies Pvt. Ltd.
Invoice Date: 2026-10-28
Due Date: 2026-11-27
Currency: INR
Subtotal: 13000.00
GST (18%): 2340.00
Total Amount Due: INR 15340.00
"""

try:
    result = extract_invoice_fields(sample_text)

    print("\nExtracted Invoice Details:")
    print(result)

except Exception as error:
    print("\nAI extraction failed:")
    print(error)
