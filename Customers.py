import json
from flask import request
from flask_restful import Resource
from flask_api import status
from datetime import datetime


class Customer(Resource):

    def __init__(self):
        try:
            with open('customers.json', 'r') as f:
                self.customers = json.load(f)
        except:
            self.customers = []
        try:
            with open('tokens.json', 'r') as f:
                self.tokens = json.load(f)
        except:
            self.tokens = {}

    def get(self):
        token = request.args.get('token')
        if token not in self.tokens:
            return {'message': 'Invalid token'}, 401
        if datetime.fromisoformat(self.tokens[token]['expires']) < datetime.utcnow():
            return {'message': 'Token expired'}, 401
        if self.tokens[token]['token_type'] != 'admin_token':
            return {'message': 'Unauthorized access, only admin users can access this method'}, 401
        return self.customers

    def post(self):

        token = request.args.get('token')
        if token not in self.tokens:
            return {'message': 'Invalid token'}, 401
        if datetime.fromisoformat(self.tokens[token]['expires']) < datetime.utcnow():
            return {'message': 'Token expired'}, 401
        if self.tokens[token]['token_type'] != 'admin_token':
            return {'message': 'Unauthorized access, only admin users can access this method'}, 401

        max_id = 0
        for entry in self.customers:
            if entry['ID'] > max_id:
                max_id = entry['ID']
        name = request.args.get('name')
        mobile = request.args.get('mobile')
        bookings = 0
        for customer in self.customers:
            # A customer is uniquely identified by their name AND mobile number
            if customer['name'] == name and customer['mobile'] == mobile:
                # Cannot add duplicate customers
                return {"message": "Customer already exists"}, status.HTTP_400_BAD_REQUEST
        cust_dict = {'ID': max_id+1, 'name': name,
                     'mobile': mobile, 'bookings': bookings}
        self.customers.append(cust_dict)
        with open("customers.json", "w") as f:
            json.dump(self.customers, f)
        return {"message": "Added Customer Successfully"}, status.HTTP_200_OK

    def delete(self):
        token = request.args.get('token')
        if token not in self.tokens:
            return {'message': 'Invalid token'}, 401
        if datetime.fromisoformat(self.tokens[token]['expires']) < datetime.utcnow():
            return {'message': 'Token expired'}, 401
        if self.tokens[token]['token_type'] != 'admin_token':
            return {'message': 'Unauthorized access, only admin users can access this method'}, 401

        name = request.args.get('name')
        if not name:
            return {"message": "Customer name cannot be blank"}, status.HTTP_400_BAD_REQUEST
        mobile = request.args.get('mobile')
        customer_to_delete = {'name': name, 'mobile': mobile}
        for i, customer in enumerate(self.customers):
            if customer['name'] == name and customer['mobile'] == mobile:
                del self.customers[i]
                with open("customers.json", "w") as f:
                    json.dump(self.customers, f)
                return {"message": "Customer deleted successfully"}, status.HTTP_200_OK
        return {"message": "Customer not found"}, status.HTTP_404_NOT_FOUND


class CustomerByName(Resource):
    def __init__(self):
        try:
            with open('customers.json', 'r') as f:
                self.customers = json.load(f)
        except:
            self.customers = []
        try:
            with open('tokens.json', 'r') as f:
                self.tokens = json.load(f)
        except:
            self.tokens = {}

    def get(self, name):
        token = request.args.get('token')
        if token not in self.tokens:
            return {'message': 'Invalid token'}, 401
        if datetime.fromisoformat(self.tokens[token]['expires']) < datetime.utcnow():
            return {'message': 'Token expired'}, 401
        if self.tokens[token]['token_type'] != 'admin_token':
            return {'message': 'Unauthorized access, only admin users can access this method'}, 401

        to_return = []
        for entry in self.customers:
            if entry['name'] == name:
                to_return.append(entry)
        return json.dumps(to_return), status.HTTP_200_OK
