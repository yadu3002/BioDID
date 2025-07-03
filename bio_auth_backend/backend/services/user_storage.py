import json
import os

USERS_FILE = "users.json"

# Load all users from local JSON storage
def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r") as f:
        return json.load(f)

# Save user list to the JSON file
def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

# Add a new user to storage
def add_user(user_dict):
    users = load_users()
    users.append(user_dict)
    save_users(users)

# Find a user by their DID
def find_user_by_did(did):
    users = load_users()
    for user in users:
        if user.get("did") == did:
            return user
    return None

def save_user_profile(user_obj):
    users = load_users()
    users.append(user_obj)
    save_users(users)

# Remove user by DID
def delete_user_by_did(did):
    users = load_users()
    users = [user for user in users if user.get("did") != did]
    save_users(users)
