from app.services.text_preprocessor import preprocess_text

sample_text = """
TAX INVOICE


Invoice Number:   INV-1004


Vendor Name:    Bright Star Supplies Pvt. Ltd.


Total Amount:   INR 12,980.00
"""

cleaned_text = preprocess_text(sample_text)

print("Original Text:")
print(sample_text)

print("\nCleaned Text:")
print(cleaned_text)