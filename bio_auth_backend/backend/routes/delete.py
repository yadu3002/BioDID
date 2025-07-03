from flask import Blueprint, request, jsonify
import os
import json
import requests
from services.user_storage import load_users, save_users

delete_bp = Blueprint("delete", __name__)

PINATA_JWT = os.environ.get("PINATA_JWT")

def delete_from_pinata(ipfs_hash):
    url = f"https://api.pinata.cloud/pinning/unpin/{ipfs_hash}"
    headers = { "Authorization": PINATA_JWT }
    response = requests.delete(url, headers=headers)
    return response.status_code == 200

@delete_bp.route("/delete_user", methods=["POST"])
def delete_user():
    data = request.get_json()
    did = data.get("did")

    if not did:
        return jsonify({ "error": "Missing DID" }), 400

    users = load_users()
    user = next((u for u in users if u["did"] == did), None)

    if not user:
        return jsonify({ "error": "User not found" }), 404

    errors = []
    for key in ["ipfsHash", "embeddingIpfsHash", "fingerprintIpfsHash"]:
        ipfs_hash = user.get(key)
        if ipfs_hash and not delete_from_pinata(ipfs_hash):
            errors.append(f"Failed to unpin {key}")

    # Remove user from list
    users = [u for u in users if u["did"] != did]
    save_users(users)

    return jsonify({
        "message": "User deleted" if not errors else "User deleted with some errors",
        "errors": errors
    })
