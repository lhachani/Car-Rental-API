from flask import request
from flask_restful import Resource
from flask_api import status
import json
from datetime import datetime


class Cars(Resource):
    TYPES = ['economic', 'standard', 'premium']
    cars = []

    def __init__(self):
        self.cars = []
        try:
            with open("cars.json", "r") as fn:
                self.cars = list(json.load(fn))
        except:
            pass
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
        return json.dumps(self.cars), status.HTTP_200_OK

    def post(self):
        token = request.args.get('token')
        if token not in self.tokens:
            return {'message': 'Invalid token'}, 401
        if datetime.fromisoformat(self.tokens[token]['expires']) < datetime.utcnow():
            return {'message': 'Token expired'}, 401
        if self.tokens[token]['token_type'] != 'admin_token':
            return {'message': 'Unauthorized access, only admin users can access this method'}, 401

        model = request.args.get('model')
        if not model:
            return {"message": "Car model cannot be blank"}, status.HTTP_400_BAD_REQUEST
        license_plate = request.args.get('license_plate')
        type = request.args.get('type')
        if type not in self.TYPES:
            return {"message": "Incorrect car type. Must belong to " + str(self.TYPES)}, status.HTTP_400_BAD_REQUEST
        fee = request.args.get('fee')
        try:
            fee = int(fee)
            if fee < 0:
                raise ValueError
        except ValueError:
            return {"message": "Fee must be a positive int value "}, status.HTTP_400_BAD_REQUEST

        car_dict = {'model': model, 'license_plate': license_plate,
                    'type': type, 'fee': fee}
        if any(car['license_plate'] == license_plate for car in self.cars):
            return {"message": "This car already exists"}, status.HTTP_400_BAD_REQUEST
        else:
            self.cars.append(car_dict)
            with open('cars.json', 'w') as fn:
                json.dump(self.cars, fn)
            return {"message": "Added Car Successfully"}, status.HTTP_200_OK

    def delete(self):
        model = request.args.get('model')
        license_plate = request.args.get('license_plate')
        token = request.args.get('token')
        if token not in self.tokens:
            return {'message': 'Invalid token'}, 401
        if datetime.fromisoformat(self.tokens[token]['expires']) < datetime.utcnow():
            return {'message': 'Token expired'}, 401
        if self.tokens[token]['token_type'] != 'admin_token':
            return {'message': 'Unauthorized access, only admin users can access this method'}, 401

        for i, car in enumerate(self.cars):
            if car['model'] == model and car['license_plate'] == license_plate:
                del self.cars[i]
                with open("cars.json", "w") as f:
                    json.dump(self.cars, f)
                return {"message": "Car deleted successfully"}, status.HTTP_200_OK
        return {"message": "Car not found"}, status.HTTP_404_NOT_FOUND


class CarByModel(Resource):

    def __init__(self):
        try:
            with open('cars.json', 'r') as f:
                self.cars = json.load(f)
        except FileNotFoundError:
            self.cars = []
        try:
            with open('tokens.json', 'r') as f:
                self.tokens = json.load(f)
        except:
            self.tokens = {}

    def get(self, model):

        token = request.args.get('token')
        if token not in self.tokens:
            return {'message': 'Invalid token'}, 401
        if datetime.fromisoformat(self.tokens[token]['expires']) < datetime.utcnow():
            return {'message': 'Token expired'}, 401

        to_return = []
        for entry in self.cars:
            if entry['model'] == model:
                to_return.append(entry)
        return json.dumps(to_return), status.HTTP_200_OK
