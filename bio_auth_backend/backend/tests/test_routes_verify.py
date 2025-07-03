import io
import json
import pytest
from flask import Flask
from routes.verify import verify_bp
from unittest.mock import patch

@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(verify_bp)
    app.config['TESTING'] = True
    return app.test_client()

@patch("routes.verify.verify_face_embedding")
@patch("routes.verify.load_users")
def test_verify_face_success(mock_load_users, mock_verify_face, client):
    dummy_user = {"did": "did:example:xyz", "name": "Alice"}
    mock_load_users.return_value = [dummy_user]
    mock_verify_face.return_value = (dummy_user, 97.5)

    response = client.post(
        "/verify_face",
        data={"image": (io.BytesIO(b"fake image data"), "face.jpg")},
        content_type="multipart/form-data"
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["message"] == "✅ Face verified"
    assert data["confidence"] == 97.5
    assert data["user"]["did"] == "did:example:xyz"

@patch("routes.verify.verify_face_embedding")
@patch("routes.verify.load_users")
def test_verify_face_failure(mock_load_users, mock_verify_face, client):
    mock_load_users.return_value = []
    mock_verify_face.return_value = (None, 0)

    response = client.post(
        "/verify_face",
        data={"image": (io.BytesIO(b"wrong image"), "face.jpg")},
        content_type="multipart/form-data"
    )

    assert response.status_code == 404
    data = json.loads(response.data)
    assert "error" in data
