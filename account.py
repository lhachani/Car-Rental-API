import json
import hashlib
from flask_restful import Resource
from flask import request
from datetime import datetime


class Account(Resource):
    def __init__(self):
        # Load existing accounts from JSON file
        try:
            with open('accounts.json', 'r') as f:
                self.accounts = json.load(f)
        except:
            self.accounts = {}
        self.tokens = self.load_tokens()

    def load_tokens(self):
        try:
            with open('tokens.json', 'r') as file:
                self.tokens = json.load(file)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            self.tokens = []
        return self.tokens

    def get(self):
        token = request.args.get('token')
        if token not in self.tokens:
            return {'message': 'Invalid token'}, 401
        if datetime.fromisoformat(self.tokens[token]['expires']) < datetime.utcnow():
            return {'message': 'Token expired'}, 401
        if self.tokens[token]['token_type'] != 'admin_token':
            return {'message': 'Unauthorized access, only admin users can access this method'}, 401
        return self.accounts

    def post(self, name, account_type, password):
        if account_type not in ['admin', 'user']:
            return {'message': 'Invalid account type'}, 400
        if name in self.accounts:
            return {'message': 'Account already exists'}, 400

        # Hash the password using sha256
        password = hashlib.sha256(password.encode()).hexdigest()
        self.accounts[name] = {
            "account_type": account_type, "password": password}

        with open('accounts.json', 'w') as f:
            json.dump(self.accounts, f)
        return {'message': 'Account created successfully'}, 201
