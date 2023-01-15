from flask import request
from flask_restful import Resource
from flask_api import status
import json
from datetime import datetime
from Cars import Cars


class Booking(Resource):

    date_format = '%d-%m-%Y'
    today = datetime.now().date()

    def __init__(self):
        self.bookings = []
        self.bookings = self.load_bookings()
        self.tokens = self.load_tokens()

    def load_bookings(self):
        try:
            with open('bookings.json', 'r') as file:
                self.bookings = json.load(file)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            self.bookings = []
        return self.bookings

    def load_tokens(self):
        try:
            with open('tokens.json', 'r') as file:
                self.tokens = json.load(file)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            self.tokens = []
        return self.tokens

    def save_bookings(self):
        with open('bookings.json', 'w') as file:
            json.dump(self.bookings, file)

    def get(self):
        token = request.args.get('token')
        if token not in self.tokens:
            return {'message': 'Invalid token'}, 401
        if datetime.fromisoformat(self.tokens[token]['expires']) < datetime.utcnow():
            return {'message': 'Token expired'}, 401
        if self.tokens[token]['token_type'] != 'admin_token':
            return {'message': 'Unauthorized access, only admin users can access this method'}, 401

        return json.dumps(self.bookings), status.HTTP_200_OK

    def fix_date(self, date_str):
        try:
            fixed_date = datetime.strptime(date_str, self.date_format).date()
        except TypeError or ValueError:
            return None
        else:
            return fixed_date

    def post(self):

        token = request.args.get('token')
        if token not in self.tokens:
            return {'message': 'Invalid token'}, 401
        if datetime.fromisoformat(self.tokens[token]['expires']) < datetime.utcnow():
            return {'message': 'Token expired'}, 401
        if self.tokens[token]['token_type'] != 'admin_token':
            return {'message': 'Unauthorized access, only admin users can access this method'}, 401

        booking_id = id(self)
        car_type = request.args.get('car')
        try:
            start_date = self.fix_date(request.args.get('start_date'))
            end_date = self.fix_date(request.args.get('end_date'))
        except ValueError:
            return {"message": "Invalid Dates Provided, please use dd-mm-yyyy"}, status.HTTP_400_BAD_REQUEST
        if start_date < self.today or end_date < start_date:
            return {"message": 'Invalid date range provided'}, status.HTTP_400_BAD_REQUEST
        if car_type not in Cars.TYPES:
            return {"message": 'Invalid car type, please enter one from ' + str(Cars.TYPES)}, \
                status.HTTP_400_BAD_REQUEST

        car_list = []
        try:
            with open("cars.json", "r") as fn:
                cars = list(json.load(fn))
        except:
            pass
        for one_car in cars:
            if one_car['type'] == car_type:
                car_list.append(one_car)
        for booking in self.bookings:
            booking_start_date = datetime.strptime(
                booking['start_date'], '%d-%m-%Y').date()
            booking_end_date = datetime.strptime(
                booking['end_date'], '%d-%m-%Y').date()
            if booking_start_date <= start_date <= booking_end_date or \
                    booking_start_date <= end_date <= booking_end_date:
                for car in car_list:
                    if booking['car'] == car:
                        car_list.remove(car)

        if len(car_list) <= 0:
            return {"message": 'No ' + str(car_type) + " cars available for this date range"}, status.HTTP_200_OK
        else:
            selected_car = car_list[0]

        selected_customer = None
        try:
            with open("customers.json", "r") as fn:
                customers = json.load(fn)
        except:
            pass
        customer = request.args.get('customer')
        for one_cust in customers:
            if one_cust['name'] == customer:
                selected_customer = one_cust
                one_cust['bookings'] += 1

        if not selected_customer:
            return {"message": 'Customer not found'}, status.HTTP_400_BAD_REQUEST

        if end_date < start_date:
            return {"message": 'End date cannot be before start date'}, status.HTTP_400_BAD_REQUEST

        booking_status = 'new'

        self.bookings.append({'booking_id': booking_id, 'customer': selected_customer, 'car': selected_car,
                              'start_date': start_date.strftime('%d-%m-%Y'), 'end_date': end_date.strftime('%d-%m-%Y'), 'status': booking_status})
        self.save_bookings()
        return {"message": "Booking " + str(booking_id) + " Added Successfully"}, status.HTTP_200_OK

    def patch(self):

        token = request.args.get('token')
        if token not in self.tokens:
            return {'message': 'Invalid token'}, 401
        if datetime.fromisoformat(self.tokens[token]['expires']) < datetime.utcnow():
            return {'message': 'Token expired'}, 401
        if self.tokens[token]['token_type'] != 'admin_token':
            return {'message': 'Unauthorized access, only admin users can access this method'}, 401

        booking_id = request.args.get('id')
        request_type = request.args.get('request')

        try:
            with open("bookings.json", "r") as fn:
                bookings = json.load(fn)
        except:
            pass

        found = False
        for booking in bookings:
            if booking['booking_id'] == int(booking_id):
                if request_type == 'pick-up':
                    if booking['status'] == 'completed':
                        return {"message": 'Booking has already been completed'}, status.HTTP_400_BAD_REQUEST
                    start_date = datetime.strptime(
                        booking['start_date'], '%d-%m-%Y')
                    end_date = datetime.strptime(
                        booking['end_date'], '%d-%m-%Y')
                    found = True
                    if datetime.combine(self.today, datetime.min.time()) < start_date and datetime.combine(self.today, datetime.min.time()) < end_date:
                        return {"message": 'Booking has not yet started, you can pickup on or after ' +
                                start_date.strftime(self.date_format)}, status.HTTP_200_OK
                    if datetime.combine(self.today, datetime.min.time()) > start_date and datetime.combine(self.today, datetime.min.time()) < end_date:
                        return {"message": 'Booking has already ended on ' + end_date.strftime(self.date_format)}, \
                            status.HTTP_200_OK
                    else:
                        booking['status'] = 'picked-up'
                        with open("bookings.json", "w") as fn:
                            json.dump(bookings, fn)
                        return {"message": 'Booking ' + str(booking_id) + ' picked up successfully'}, status.HTTP_200_OK
                elif request_type == 'drop-off':
                    if booking['status'] == 'completed':
                        return {"message": 'Booking has already been completed'}, status.HTTP_400_BAD_REQUEST
                    elif booking['status'] == 'new':
                        return {"message": 'Booking has not yet been picked up'}, status.HTTP_400_BAD_REQUEST
                    else:
                        booking['status'] = 'completed'
                        with open("bookings.json", "w") as fn:
                            json.dump(bookings, fn)
                        return {"message": 'Booking ' + str(booking_id) + ' returned successfully'}, status.HTTP_200_OK
        if not found:
            return {"message": 'Booking not found'}, status.HTTP_404_NOT_FOUND
        else:
            return {"message": "Invalid request type, please enter either 'pick-up' or 'return'"}, status.HTTP_400_BAD_REQUEST


class BookingById(Resource):
    def __init__(self):
        self.bookings = self.load_bookings()
        self.tokens = self.load_tokens()

    def load_bookings(self):
        try:
            with open('bookings.json', 'r') as file:
                bookings = json.load(file)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            bookings = []
        return bookings

    def save_bookings(self):
        with open('bookings.json', 'w') as file:
            json.dump(self.bookings, file)

    def load_tokens(self):
        try:
            with open('tokens.json', 'r') as file:
                self.tokens = json.load(file)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            self.tokens = []
        return self.tokens

    def get(self, id):
        token = request.args.get('token')
        if token not in self.tokens:
            return {'message': 'Invalid token'}, 401
        if datetime.fromisoformat(self.tokens[token]['expires']) < datetime.utcnow():
            return {'message': 'Token expired'}, 401
        if self.tokens[token]['token_type'] != 'admin_token':
            return {'message': 'Unauthorized access, only admin users can access this method'}, 401

        for booking in self.bookings:
            if booking['booking_id'] == int(id):
                return json.dumps(booking, default=str), status.HTTP_200_OK
        return {"message": "No booking found for this id"}, status.HTTP_200_OK


class BookingByCustomer(Resource):
    def __init__(self):
        self.bookings = self.load_bookings()
        self.tokens = self.load_tokens()

    def load_tokens(self):
        try:
            with open('tokens.json', 'r') as file:
                self.tokens = json.load(file)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            self.tokens = []
        return self.tokens

    def load_bookings(self):
        try:
            with open('bookings.json', 'r') as file:
                bookings = json.load(file)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            bookings = []
        return bookings

    def save_bookings(self):
        with open('bookings.json', 'w') as file:
            json.dump(self.bookings, file)

    def get(self, name):
        token = request.args.get('token')
        if token not in self.tokens:
            return {'message': 'Invalid token'}, 401
        if datetime.fromisoformat(self.tokens[token]['expires']) < datetime.utcnow():
            return {'message': 'Token expired'}, 401
        if self.tokens[token]['token_type'] != 'admin_token':
            return {'message': 'Unauthorized access, only admin users can access this method'}, 401

        customer_bookings = []
        for booking in self.bookings:
            customer = booking['customer']
            if customer['name'] == name:
                customer_bookings.append(booking)

        if len(customer_bookings) <= 0:
            return {"message": "No bookings found for customer " + name}, status.HTTP_200_OK
        else:
            return json.dumps(customer_bookings, default=str), status.HTTP_200_OK
