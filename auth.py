import json
import hashlib
import os

USERS_FILE = 'users.json'

# Função para hashear a senha
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Função para carregar utilizadores, com verificação de existência do ficheiro
def load_users(filepath=USERS_FILE):
    if not os.path.exists(filepath):
        return {}  # Retorna um dicionário vazio se o ficheiro não existir
    with open(filepath, 'r') as f:
        return json.load(f)

# Função para guardar utilizadores num ficheiro
def save_users(users, filepath=USERS_FILE):
    with open(filepath, 'w') as f:
        json.dump(users, f, indent=4)

# Função de autenticação de utilizador
def authenticate(username, password, users):
    user = users.get(username)
    if user and user['password'] == hash_password(password):
        return user['role'], user.get('first_login', False)  # Retorna role e first_login
    return None, None  # Caso falhe, retorna None

# Função para atualizar a senha de um utilizador
def update_password(username, new_password, users):
    if username in users:
        users[username]['password'] = hash_password(new_password)
        users[username]['first_login'] = False
        save_users(users)
        return True
    return False

# Função para adicionar um novo utilizador
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

# Função para eliminar um utilizador
def delete_user(username, users):
    if username in users:
        del users[username]
        save_users(users)
        return True
    return False
