import json
import pytest
from flask import Flask
from unittest.mock import patch
from routes.delete import delete_bp

@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(delete_bp)
    app.config["TESTING"] = True
    return app.test_client()

@patch("routes.delete.save_users")
@patch("routes.delete.load_users")
@patch("routes.delete.delete_from_pinata")
def test_delete_user_success(mock_delete_pinata, mock_load_users, mock_save_users, client):
    mock_delete_pinata.return_value = True
    mock_load_users.return_value = [
        {
            "did": "did:example:123",
            "ipfsHash": "QmHash1",
            "embeddingIpfsHash": "QmHash2",
            "fingerprintIpfsHash": "QmHash3"
        }
    ]

    response = client.post(
        "/delete_user",
        data=json.dumps({"did": "did:example:123"}),
        content_type="application/json"
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["message"].startswith("User deleted")

@patch("routes.delete.load_users")
def test_delete_user_missing_did(mock_load_users, client):
    response = client.post(
        "/delete_user",
        data=json.dumps({}),  # no DID
        content_type="application/json"
    )
    assert response.status_code == 400
    assert "Missing DID" in response.get_data(as_text=True)

@patch("routes.delete.load_users")
def test_delete_user_not_found(mock_load_users, client):
    mock_load_users.return_value = []

    response = client.post(
        "/delete_user",
        data=json.dumps({"did": "did:example:doesnotexist"}),
        content_type="application/json"
    )

    assert response.status_code == 404
    data = json.loads(response.data)
    assert data["error"] == "User not found"
