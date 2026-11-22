from app.services.query_rewrite import rewrite_query
from app.core.config import GEMINI_API_KEY
#GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

query = "How much did we pay ABC in the latest invoice?"

rewritten_query = rewrite_query(query)

print("\nOriginal Query:")
print(query)

print("\nRewritten Query:")
print(rewritten_query)