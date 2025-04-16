import json
<<<<<<< HEAD
import hashlib
import os

USERS_FILE = 'users.json'

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def load_users(filepath=USERS_FILE):
    if not os.path.exists(filepath):
        return {}
    with open(filepath, 'r') as f:
        return json.load(f)

def save_users(users, filepath=USERS_FILE):
    with open(filepath, 'w') as f:
        json.dump(users, f, indent=4)

def authenticate(username, password, users):
    user = users.get(username)
    if user and user['password'] == hash_password(password):
        return user['role'], user.get('first_login', False)
    return None, None

def update_password(username, new_password, users):
    if username in users:
        users[username]['password'] = hash_password(new_password)
        users[username]['first_login'] = False
        save_users(users)
        return True
    return False

def add_user(username, password, role, users):
    if username not in users:
        users[username] = {
            "password": hash_password(password),
            "role": role,
            "first_login": True
        }
        save_users(users)
        return True
    return False

def delete_user(username, users):
    if username in users:
        del users[username]
        save_users(users)
        return True
    return False
=======

def load_users(filepath='users.json'):
    with open(filepath, 'r') as f:
        return json.load(f)

def authenticate(username, password, users):
    user = users.get(username)
    if user and user['password'] == password:
        return user['role']
    return None
>>>>>>> f387d02934759f739ea849e67344de78c7bd2682
