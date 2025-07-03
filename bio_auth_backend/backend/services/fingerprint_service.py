import os
import cv2
import json
import base64
import numpy as np
import hashlib
import requests
import re
from utils.minutiae_matching import match, Minutia
from utils.fingerprints_matching import FingerprintsMatching
from utils.ipfs_utils import upload_to_ipfs, fetch_from_ipfs
from utils.encryption_utils import encrypt_json_string, decrypt_json_string
from time import time
start = time()



from dotenv import dotenv_values

def get_aes_key():
    key = os.environ.get("AES_KEY")
    if not key:
        raise EnvironmentError("AES_KEY is not set in environment variables.")
    return base64.b64decode(key)
config = dotenv_values(".env")
PINATA_JWT = os.environ.get("PINATA_JWT")

def enhance_fingerprint(img):
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(img)
    blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
    binary = cv2.adaptiveThreshold(blurred, 255,
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 15, 8)
    return binary

def skeletonize(img):
    _, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    skel = np.zeros(img.shape, np.uint8)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    while True:
        open_img = cv2.morphologyEx(binary, cv2.MORPH_OPEN, element)
        temp = cv2.subtract(binary, open_img)
        eroded = cv2.erode(binary, element)
        skel = cv2.bitwise_or(skel, temp)
        binary = eroded.copy()
        if cv2.countNonZero(binary) == 0:
            break
    return skel

def extract_minutiae(skel_img):
    minutiae = []
    rows, cols = skel_img.shape
    for i in range(1, rows - 1):
        for j in range(1, cols - 1):
            if skel_img[i, j] == 255:
                neighbors = [
                    skel_img[i-1, j-1], skel_img[i-1, j], skel_img[i-1, j+1],
                    skel_img[i, j+1], skel_img[i+1, j+1], skel_img[i+1, j],
                    skel_img[i+1, j-1], skel_img[i, j-1]
                ]
                transitions = 0
                for k in range(len(neighbors)):
                    if neighbors[k] == 0 and neighbors[(k + 1) % 8] == 255:
                        transitions += 1
                if transitions == 1:
                    minutiae.append({'type': 'ending', 'x': j, 'y': i})
                elif transitions == 3:
                    minutiae.append({'type': 'bifurcation', 'x': j, 'y': i})
    return minutiae

def process_fingerprint_and_upload(image_bytes, did):
    safe_did = re.sub(r'[^\w\-]', '_', did)
    img_array = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)

    enhanced = enhance_fingerprint(img)
    skeleton = skeletonize(enhanced)
    minutiae = extract_minutiae(skeleton)

    data = {
        'minutiae': minutiae,
        'size': {'width': img.shape[1], 'height': img.shape[0]}
    }

    raw_json = json.dumps(data)
    hash_val = hashlib.sha256(json.dumps(minutiae).encode()).hexdigest()

    encrypted = encrypt_json_string(raw_json, get_aes_key())

    filename = f"{safe_did}_fingerprint.enc"
    ipfs_hash = upload_to_ipfs(encrypted, filename)

    return ipfs_hash, hash_val, len(minutiae)


def fingerprint_pipeline_from_bytes_encrypted(image_bytes, aes_key, output_path="encrypted_fingerprint.enc"):
    img_array = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)

    if img is None:
        raise ValueError()

    # Enhance image
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(img)
    blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
    binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 8)

    # Skeletonize
    skel = np.zeros(binary.shape, np.uint8)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    while True:
        open_img = cv2.morphologyEx(binary, cv2.MORPH_OPEN, element)
        temp = cv2.subtract(binary, open_img)
        eroded = cv2.erode(binary, element)
        skel = cv2.bitwise_or(skel, temp)
        binary = eroded.copy()
        if cv2.countNonZero(binary) == 0:
            break

    # Extract minutiae
    minutiae = []
    for i in range(1, skel.shape[0] - 1):
        for j in range(1, skel.shape[1] - 1):
            if skel[i, j] == 255:
                neighbors = [
                    skel[i-1, j-1], skel[i-1, j], skel[i-1, j+1],
                    skel[i, j+1], skel[i+1, j+1], skel[i+1, j],
                    skel[i+1, j-1], skel[i, j-1]
                ]
                transitions = sum(
                    (neighbors[k] == 0 and neighbors[(k + 1) % 8] == 255)
                    for k in range(8)
                )
                if transitions == 1:
                    minutiae.append({'type': 'ending', 'x': j, 'y': i})
                elif transitions == 3:
                    minutiae.append({'type': 'bifurcation', 'x': j, 'y': i})

    # Encrypt + hash
    fingerprint_data = {
        'minutiae': minutiae,
        'size': {'width': img.shape[1], 'height': img.shape[0]}
    }
    raw_json = json.dumps(fingerprint_data)
    encrypted = encrypt_json_string(raw_json, aes_key)
    hash_val = hashlib.sha256(raw_json.encode()).hexdigest()

    # Upload
    ipfs_hash = upload_to_ipfs(encrypted, os.path.basename(output_path))

    return ipfs_hash, hash_val, len(minutiae)


def fingerprint_pipeline_from_bytes(image_bytes):
    img_array = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)

    # Enhance image
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(img)
    blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
    binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 15, 8)

    # Skeletonize
    skel = np.zeros(binary.shape, np.uint8)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    while True:
        open_img = cv2.morphologyEx(binary, cv2.MORPH_OPEN, element)
        temp = cv2.subtract(binary, open_img)
        eroded = cv2.erode(binary, element)
        skel = cv2.bitwise_or(skel, temp)
        binary = eroded.copy()
        if cv2.countNonZero(binary) == 0:
            break

    # Extract minutiae
    minutiae = []
    for i in range(1, skel.shape[0] - 1):
        for j in range(1, skel.shape[1] - 1):
            if skel[i, j] == 255:
                neighbors = [
                    skel[i-1, j-1], skel[i-1, j], skel[i-1, j+1],
                    skel[i, j+1], skel[i+1, j+1], skel[i+1, j],
                    skel[i+1, j-1], skel[i, j-1]
                ]
                transitions = sum(
                    (neighbors[k] == 0 and neighbors[(k + 1) % 8] == 255)
                    for k in range(8)
                )
                if transitions == 1:
                    minutiae.append({'type': 'ending', 'x': j, 'y': i})
                elif transitions == 3:
                    minutiae.append({'type': 'bifurcation', 'x': j, 'y': i})

    hash_val = hashlib.sha256(json.dumps(minutiae).encode()).hexdigest()
    return img, hash_val, minutiae
print(f"Fingerprint time: {round(time() - start, 2)}s")


def verify_fingerprint_minutiae(uploaded_bytes, users, AES_KEY):
    # Decode fingerprint image from bytes to grayscale image
    img_array = np.frombuffer(uploaded_bytes, np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)

    if img is None:
        raise ValueError("Could not decode image from bytes")

    # Preprocess: Enhance and skeletonize
    enhanced = enhance_fingerprint(img)
    skeleton = skeletonize(enhanced)

    # Extract minutiae from skeleton
    extracted_raw = extract_minutiae(skeleton)
    uploaded_points = [Minutia(m['x'], m['y'], 0, m['type']) for m in extracted_raw]

    best_match = None
    highest_score = 0

    for user in users:
        if not user.get("fingerprintIpfsHash"):
            continue

        try:
            encrypted_data = fetch_from_ipfs(user["fingerprintIpfsHash"])
            decrypted_data = decrypt_json_string(encrypted_data, AES_KEY)

            if isinstance(decrypted_data, str):
                parsed = json.loads(decrypted_data)
            else:
                parsed = decrypted_data

            stored_raw = parsed.get("minutiae", [])
            stored_points = [Minutia(m['x'], m['y'], 0, m['type']) for m in stored_raw]


            score = match(uploaded_points, stored_points)
            print(f"[🔍] Compared with {user['name']} - Score: {score:.2f}")

            if score > highest_score:
                highest_score = score
                best_match = user
        except Exception as e:
            print(f" Error comparing with {user['name']}: {e}")

    return best_match, highest_score
