import base64
import json
import os
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
from time import time

from services.face_service import capture_and_encrypt_face_embedding
from services.fingerprint_service import fingerprint_pipeline_from_bytes_encrypted
from services.user_storage import save_user_profile

load_dotenv()
start = time()

# Decode AES key once for reuse
aes_key_raw = base64.b64decode(os.environ.get("AES_KEY"))
register_bp = Blueprint('register', __name__)

# Route to handle encrypted face registration and IPFS upload
@register_bp.route('/register_face', methods=['POST'])
def register_face():
    try:
        image = request.files['image']
        did = request.form['did']
        ipfs_hash, face_hash = capture_and_encrypt_face_embedding(image.read(), did)

        return jsonify({
            "message": "Face embedding uploaded to IPFS",
            "embeddingIpfsHash": ipfs_hash,
            "embeddingHash": face_hash
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Route to upload and process encrypted fingerprint data
@register_bp.route('/upload_fingerprint', methods=['POST'])
def upload_fingerprint():
    try:
        fingerprint = request.files['fingerprint']
        did = request.form['did']

        if not aes_key_raw:
            return jsonify({"error": "AES_KEY not set"}), 500

        ipfs_hash, minutiae_hash, count = fingerprint_pipeline_from_bytes_encrypted(
            fingerprint.read(),
            aes_key_raw
        )

        return jsonify({
            "message": "Fingerprint encrypted and uploaded",
            "fingerprintIpfsHash": ipfs_hash,
            "fingerprintHash": minutiae_hash,
            "minutiaeCount": count
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to create and save a new user profile
@register_bp.route('/create_user', methods=['POST'])
def create_user():
    try:
        data = request.json

        required = ['did', 'name', 'embeddingIpfsHash', 'embeddingHash']
        if not all(k in data for k in required):
            return jsonify({"error": "Missing required fields"}), 400

        user = {
            "did": data['did'],
            "name": data['name'],
            "embeddingIpfsHash": data['embeddingIpfsHash'],
            "faceTemplateHash": data['embeddingHash'],
            "fingerprintIpfsHash": data.get("fingerprintIpfsHash"),
            "fingerprintHash": data.get("fingerprintHash"),
            "anchoredTx": data.get("anchoredTx"),
            "createdAt": data.get("createdAt")
        }

        save_user_profile(user)
        return jsonify({"message": "User profile saved"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

print(f"Register blueprint load time: {round(time() - start, 2)}s")
