import pytest
import json
from unittest.mock import mock_open, patch
from services.user_storage import load_users, save_users, add_user, find_user_by_did, delete_user_by_did

dummy_users = [
    {"did": "did:example:123", "name": "Alice"},
    {"did": "did:example:456", "name": "Bob"},
]

@patch("builtins.open", new_callable=mock_open, read_data=json.dumps(dummy_users))
@patch("os.path.exists", return_value=True)
def test_load_users(mock_exists, mock_open_file):
    users = load_users()
    assert isinstance(users, list)
    assert users[0]["name"] == "Alice"

@patch("builtins.open", new_callable=mock_open)
def test_save_users(mock_open_file):
    save_users(dummy_users)
    mock_open_file.assert_called_once_with("users.json", "w")
    handle = mock_open_file()
    handle.write.assert_called()

@patch("builtins.open", new_callable=mock_open, read_data=json.dumps(dummy_users))
@patch("os.path.exists", return_value=True)
def test_find_user_by_did(mock_exists, mock_open_file):
    user = find_user_by_did("did:example:456")
    assert user is not None
    assert user["name"] == "Bob"

@patch("builtins.open", new_callable=mock_open)
@patch("services.user_storage.load_users", return_value=dummy_users)
def test_delete_user_by_did(mock_load, mock_open_file):
    delete_user_by_did("did:example:123")
    handle = mock_open_file()
    handle.write.assert_called()
    all_calls = handle.write.call_args_list
    written_str = "".join(call.args[0] for call in all_calls)
    saved_json = json.loads(written_str)
    assert not any(user["did"] == "did:example:123" for user in saved_json)

