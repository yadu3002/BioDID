import io
import json
import pytest
from flask import Flask
from unittest.mock import patch
from routes.register import register_bp

@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(register_bp)
    app.config["TESTING"] = True
    return app.test_client()

@patch("routes.register.capture_and_encrypt_face_embedding")
def test_register_face_success(mock_encrypt, client):
    mock_encrypt.return_value = ("QmFakeIpfsHash", "facehash123")

    response = client.post(
        "/register_face",
        data={
            "image": (io.BytesIO(b"fake_face_image_data"), "face.jpg"),
            "did": "did:example:test"
        },
        content_type="multipart/form-data"
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert "embeddingIpfsHash" in data
    assert "embeddingHash" in data


@patch("routes.register.capture_and_encrypt_face_embedding", side_effect=Exception("No face found"))
def test_register_face_failure(mock_encrypt, client):
    response = client.post(
        "/register_face",
        data={
            "image": (io.BytesIO(b"bad_data"), "face.jpg"),
            "did": "did:example:test"
        },
        content_type="multipart/form-data"
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
