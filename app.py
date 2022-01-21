from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from flask_jwt import JWT, jwt_required
from security import authenticate, identity

app = Flask(__name__)
app.secret_key = 'veryverysecretkey'
api = Api(app)

jwt = JWT(app, authenticate, identity)  # '/auth'

items = []


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
                        type=float,
                        required=True,
                        help='This field cannot be left blank!'
                        )

    @jwt_required()
    def get(self, name):
        item = next(filter(lambda i: i['name'] == name, items))
        return {'Item': item}, 200 if item else 404

    @jwt_required()
    def post(self, name):
        if next(filter(lambda i: i['name'] == name, items), None):
            return {'message': f"An item with name '{name}' already exists"}, 400
        data = Item.parser.parse_args()
        item = {"name": name, "price": data["price"]}
        items.append(item)
        return item, 201

    @jwt_required()
    def delete(self, name):
        global items
        items = list(filter(lambda i: i['name'] != name, items))
        return {'message': 'Item deleted'}

    @jwt_required()
    def put(self, name):
        data = Item.parser.parse_args()

        item = next(filter(lambda i: i['name'] == name, items), None)
        if item is None:
            item = {"name": name, "price": data["price"]}
            items.append(item)
        else:
            item.update(data)
        return item


class ItemList(Resource):
    def get(self):
        if items:
            return {'items': items}, 200
        return {'Items': None}, 404


api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')

app.run(port=5000, debug=True)
