import pytest
import json
import os
import base64
from utils.encryption_utils import encrypt_json_string, decrypt_json_string

# Set dummy AES_KEY if not present (32 bytes base64 string)
# Convert string → bytes → base64 → string
dummy_key_bytes = b"bd66UOfztArWqjsItjrUZ293FeTE77fo"  # 32 bytes
os.environ["AES_KEY"] = base64.b64encode(dummy_key_bytes).decode()


# Sample test dictionary
sample_data = {"embedding": [0.1] * 128}
sample_json = json.dumps(sample_data)

# Decode the AES key for use
AES_KEY = base64.b64decode(os.environ.get("AES_KEY"))

def test_encryption_and_decryption_round_trip():
    encrypted = encrypt_json_string(sample_json, AES_KEY)
    assert "iv" in encrypted and "ciphertext" in encrypted

    decrypted = decrypt_json_string(encrypted, AES_KEY)
    assert decrypted["embedding"] == [0.1] * 128
