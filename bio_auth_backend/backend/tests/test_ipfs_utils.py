import os
import json
import pytest
from unittest.mock import patch, mock_open
from utils.ipfs_utils import upload_to_ipfs, fetch_from_ipfs

# Set a dummy PINATA_JWT so the code doesn't fail
os.environ["PINATA_JWT"] = "Bearer test_token"

@pytest.fixture
def dummy_data():
    return {"test": "value"}

@patch("utils.ipfs_utils.requests.post")
@patch("builtins.open", new_callable=mock_open)
@patch("os.remove")
def test_upload_to_ipfs(mock_remove, mock_open_file, mock_post, dummy_data):
    # Mock Pinata response
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"IpfsHash": "QmDummyHash"}

    ipfs_hash = upload_to_ipfs(dummy_data, filename="test.json")

    assert ipfs_hash == "QmDummyHash"
    mock_remove.assert_called_once()

@patch("utils.ipfs_utils.requests.get")
def test_fetch_from_ipfs(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"hello": "world"}

    result = fetch_from_ipfs("QmDummyHash")

    assert result == {"hello": "world"}
