import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from app.services.invoice_agent import get_sample_api_data


result = get_sample_api_data(1)

print(result)