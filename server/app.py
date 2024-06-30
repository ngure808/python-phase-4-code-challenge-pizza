#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.serialize() for restaurant in restaurants])

@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = db.session.get(Restaurant, id)
    if restaurant:
        return jsonify(restaurant.serialize(include_pizzas=True))
    else:
        return jsonify({'error': 'Restaurant not found'}), 404
    
@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant_by_id(id):
    restaurant = db.session.get(Restaurant,id)

    if restaurant:
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204 
    else:
        return jsonify({'error': 'Restaurant not found'}), 404
    
@app.route('/pizzas', methods = ["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.serialize() for pizza in pizzas])

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizzas():
    data = request.json

    # Extract data from request
    price = data.get('price')
    pizza_id = data.get('pizza_id')
    restaurant_id = data.get('restaurant_id')
    
    #validates entry of price
    if not (1 <= price <= 30):
        return jsonify({'errors': ["validation errors"]}), 400

    # Create new RestaurantPizza instance
    new_entry = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)

    try:
        db.session.add(new_entry)
        db.session.commit()
        return jsonify({
            'id': new_entry.id,
            'price': new_entry.price,
            'pizza_id': new_entry.pizza_id,
            'restaurant_id': new_entry.restaurant_id,
            'pizza': new_entry.pizza.serialize() if new_entry.pizza else None,
            'restaurant': new_entry.restaurant.serialize() if new_entry.restaurant else None
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400




if __name__ == "__main__":
    app.run(port=5555, debug=True)
