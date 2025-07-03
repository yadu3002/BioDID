import base64
import json
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# Retrieves the AES key from environment variables
def get_aes_key():
    key = os.environ.get("AES_KEY")
    if not key:
        raise EnvironmentError("AES_KEY is not set in environment variables.")
    return base64.b64decode(key)

# Encrypts a JSON string using AES (CBC mode)
def encrypt_json_string(json_string, aes_key=None):
    if aes_key is None:
        aes_key = get_aes_key()
    cipher = AES.new(aes_key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(json_string.encode(), AES.block_size))
    return {
        "iv": base64.b64encode(cipher.iv).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode()
    }

# Decrypts AES-encrypted JSON back to a Python dictionary
def decrypt_json_string(encrypted_json, aes_key=None):
    if aes_key is None:
        aes_key = get_aes_key()
    iv = base64.b64decode(encrypted_json["iv"])
    ciphertext = base64.b64decode(encrypted_json["ciphertext"])
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return json.loads(plaintext.decode())
