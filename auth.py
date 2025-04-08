import json

def load_users(filepath='users.json'):
    with open(filepath, 'r') as f:
        return json.load(f)

def authenticate(username, password, users):
    user = users.get(username)
    if user and user['password'] == password:
        return user['role']
    return None
