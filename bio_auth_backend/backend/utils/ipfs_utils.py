import os
import json
import requests

# Uploads a JSON-compatible dictionary to IPFS via Pinata
def upload_to_ipfs(data_dict, filename="data.json"):
    PINATA_JWT = os.environ.get("PINATA_JWT")
    if not PINATA_JWT:
        raise EnvironmentError("PINATA_JWT not set in environment variables.")

    temp_path = f"./temp_uploads/{filename}"
    os.makedirs("temp_uploads", exist_ok=True)

    # Save data to a temporary JSON file
    with open(temp_path, "w") as f:
        json.dump(data_dict, f)

    try:
        with open(temp_path, "rb") as file_data:
            files = {
                'file': (filename, file_data, 'application/json')
            }
            headers = {
                'Authorization': PINATA_JWT
            }

            response = requests.post(
                'https://api.pinata.cloud/pinning/pinFileToIPFS',
                files=files,
                headers=headers
            )

        if response.status_code == 200:
            return response.json().get("IpfsHash")
        else:
            raise Exception(f"Pinata upload failed: {response.text}")

    finally:
        os.remove(temp_path)

# Fetches and parses a JSON object from a public IPFS gateway
def fetch_from_ipfs(ipfs_hash):
    gateways = [
        f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}",
        f"https://dweb.link/ipfs/{ipfs_hash}"
    ]

    for url in gateways:
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                return res.json()
        except Exception:
            continue  # Try next gateway if fetch fails

    return None
