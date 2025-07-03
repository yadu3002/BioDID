import base64
import os
from flask import Blueprint, request, jsonify
from dotenv import dotenv_values

from services.user_storage import load_users
from services.face_service import verify_face_embedding
from services.fingerprint_service import verify_fingerprint_minutiae

verify_bp = Blueprint("verify", __name__)

# Load AES key from environment
config = dotenv_values(".env")
AES_KEY = base64.b64decode(config["AES_KEY"])

# Endpoint for face-based identity verification
@verify_bp.route("/verify_face", methods=["POST"])
def verify_face():
    image = request.files.get("image")
    if not image:
        return jsonify({"error": "Image file is required"}), 400

    users = load_users()
    user, confidence = verify_face_embedding(image.read(), users)

    if user:
        return jsonify({
            "message": "Face verified successfully",
            "user": user,
            "confidence": round(confidence, 2)
        })
    else:
        return jsonify({"error": "Face not recognized"}), 404

# Endpoint for fingerprint-based identity verification
@verify_bp.route("/verify_fingerprint", methods=["POST"])
def verify_fingerprint():
    fingerprint = request.files.get("fingerprint")
    if not fingerprint:
        return jsonify({"error": "Fingerprint file is required"}), 400

    users = load_users()
    user, similarity = verify_fingerprint_minutiae(fingerprint.read(), users, AES_KEY)


    if user and similarity > 0.75:
        print(f"[✅] Matched user: {user['name']} with similarity: {similarity}")
        return jsonify({"status": "success", "user": user['name'], "similarity": similarity}), 200
    else:
        return jsonify({"status": "failed", "message": "No matching fingerprint found", "similarity": similarity}), 404

