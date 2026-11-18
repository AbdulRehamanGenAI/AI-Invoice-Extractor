from app.services.embedding_service import generate_embedding

text = "Invoice INV-1002 from Bright Star Supplies Pvt. Ltd. Total amount INR 9440."

embedding = generate_embedding(text)

print("Embedding dimensions:", len(embedding))
print("First five values:", embedding[:5])