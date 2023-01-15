from flask import Flask
from flask_restful import Api
from Cars import Cars, CarByModel
from Customers import Customer, CustomerByName
from Booking import Booking, BookingById, BookingByCustomer
from account import Account
from accesstoken import Token


app = Flask(__name__)
api = Api(app)


# The home page of the API
@app.route('/')
def api_root():
    return '<h1>Welcome to CarRentalApi</h1><br /> <hr>' \



def add_resources():
    api.add_resource(Customer, '/customers')
    api.add_resource(CustomerByName, '/customers/<name>')
    api.add_resource(Cars, '/cars')
    api.add_resource(CarByModel, '/cars/<model>')
    api.add_resource(Booking, '/booking')
    api.add_resource(BookingById, '/booking/searchbyid/<id>')
    api.add_resource(BookingByCustomer, '/booking/searchbycustomer/<name>')
    api.add_resource(Account, '/account/',
                     '/account/<string:name>/<string:account_type>/<string:password>')
    api.add_resource(Token, '/token/',
                     '/token/<string:name>/<string:password>')


if __name__ == '__main__':
    add_resources()
    app.run(port='5002', debug=True)
