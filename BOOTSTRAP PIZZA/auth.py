from flask import current_app
from models import User
from db import users

def load_user(email):
    if email not in users:
        return None
    user = User()
    user.id = email
    return user

def authenticate(email, password):
    if email in users and users[email]["password"] == password:
        return True
    return False

def is_authenticated():
    return current_app.login_manager._login_disabled