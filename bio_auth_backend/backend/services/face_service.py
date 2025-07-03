import json
import base64
import numpy as np
import hashlib
import os
import re
import cv2
import face_recognition

from dotenv import dotenv_values
from time import time
from io import BytesIO

from utils.encryption_utils import encrypt_json_string, decrypt_json_string
from utils.ipfs_utils import upload_to_ipfs, fetch_from_ipfs

# Load environment
config = dotenv_values(".env")
start = time()

def get_aes_key():
    key = os.environ.get("AES_KEY")
    if not key:
        raise EnvironmentError("AES_KEY is not set in environment variables.")
    return base64.b64decode(key)

# Extract face embedding from raw image bytes
def extract_face_embedding(image_bytes):
    npimg = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    face_locations = face_recognition.face_locations(img)

    if not face_locations:
        raise Exception("No face detected")

    embedding = face_recognition.face_encodings(img, face_locations)[0].tolist()
    return embedding

# Encrypt and upload a new embedding to IPFS
def capture_and_encrypt_face_embedding(image_bytes, did):
    embedding = extract_face_embedding(image_bytes)
    payload = json.dumps({"embedding": embedding})
    encrypted = encrypt_json_string(payload, get_aes_key())

    safe_did = re.sub(r"[^\w\-]", "_", did)
    filename = f"{safe_did}_face.enc"

    ipfs_hash = upload_to_ipfs(encrypted, filename)
    face_hash = hashlib.sha256(payload.encode()).hexdigest()

    return ipfs_hash, face_hash

# Match input image to stored embeddings from IPFS
def verify_face_embedding(image_bytes, users_data):
    embedding = extract_face_embedding(image_bytes)
    input_vector = np.array(embedding)

    best_user = None
    best_dist = float("inf")

    for user in users_data:
        ipfs_hash = user.get("embeddingIpfsHash")
        if not ipfs_hash:
            continue

        raw_encrypted = fetch_from_ipfs(ipfs_hash)
        if not raw_encrypted or "iv" not in raw_encrypted:
            continue

        parsed = decrypt_json_string(raw_encrypted, get_aes_key())
        if "embedding" not in parsed:
            continue

        stored = np.array(parsed["embedding"])
        dist = np.linalg.norm(input_vector - stored)

        if dist < best_dist:
            best_dist = dist
            best_user = user

    if best_user:
        confidence = max(0, 100 - (best_dist * 100))
        return best_user, confidence
    else:
        return None, 0

print(f"Face service execution time: {round(time() - start, 2)}s")
