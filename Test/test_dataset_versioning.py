import hashlib
from pathlib import Path


def calculate_dataset_hash(dataset_path):
    dataset_bytes = Path(dataset_path).read_bytes()
    dataset_hash = hashlib.sha256(dataset_bytes).hexdigest()
    return dataset_hash


def test_dataset_hash_is_generated():
    dataset_path = "datasets/invoice_eval.jsonl"
    dataset_hash = calculate_dataset_hash(dataset_path)
    assert len(dataset_hash) == 64
    print("Dataset SHA256:", dataset_hash)