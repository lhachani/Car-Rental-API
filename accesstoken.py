import json
import uuid
import hashlib
from datetime import datetime, timedelta
from flask_restful import Resource


class Token(Resource):
    def __init__(self):
        # Load existing accounts from JSON file
        try:
            with open('accounts.json', 'r') as f:
                self.accounts = json.load(f)
        except:
            self.accounts = {}
        try:
            with open('tokens.json', 'r') as f:
                self.tokens = json.load(f)
        except:
            self.tokens = {}

    def post(self, name, password):
        # Check if the account exists and the password is correct
        if name not in self.accounts or self.accounts[name]['password'] != hashlib.sha256(password.encode()).hexdigest():
            return {'message': 'Invalid credentials'}, 401
        user_type = self.accounts[name]['user_type']
        # Create a new token based on account_type
        if user_type == 'admin':
            token_type = 'admin_token'
        elif user_type == 'user':
            token_type = 'user_token'
        else:
            return {'message': 'Invalid account type'}, 401
        token = str(uuid.uuid4())
        expires = datetime.utcnow() + timedelta(minutes=30)
        self.tokens[token] = {
            'name': name, 'expires': expires.isoformat(), 'token_type': token_type}
        with open('tokens.json', 'w') as f:
            json.dump(self.tokens, f)
        return {'token': token, 'expires': expires.isoformat(), 'token_type': token_type}, 201
