from flask import Response, request, Blueprint, jsonify, abort
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError
from flask_mongoengine import MongoEngine, Pagination
from flasgger import swag_from
from mongoengine.errors import ValidationError as VError
from bson import ObjectId

from src.auth import app_jwt_required
from src.database import User, Restaurant, RestaurantSchema, db
from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_409_CONFLICT, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN, HTTP_503_SERVICE_UNAVAILABLE

from common import paginator_service, errorResponse

restaurant = Blueprint("restaurant", __name__, url_prefix="/api/v1/restaurant")


@restaurant.get("/")
@app_jwt_required()
@swag_from("./docs/restaurant/list.yaml")
def restaurant_list():
    per_page = request.args.get('perPage') if request.args.get(
        'perPage') != None else 10
    current_page = request.args.get('currentPage') if request.args.get(
        'currentPage') != None else 1

    lat = request.args.get('lat')
    lng = request.args.get('lng')

    if not lat or not lng:
        return errorResponse("Lat & Lng Field is required.", 422)

    # 27.719622795070237, 85.30442831534448

    custom_query = (Restaurant.objects.get_restro_nearby(lat, lng))

    items = []

    for item in custom_query:
        item['_id'] = str(item['_id'])
        item = Restaurant.parser_object(item)
        items.append(item)

    paginator = Pagination(items, int(current_page), int(per_page))
    return paginator_service(paginator, paginator.items)


@restaurant.post("/")
@app_jwt_required()
@swag_from("./docs/restaurant/store.yaml")
def create():
    user = User.objects(id=get_jwt_identity()).first()
    body = request.get_json()
    schema = RestaurantSchema()
    try:
        data = schema.load(body)
        restaurant = Restaurant(**body).save()
        return jsonify({
            "data": restaurant.object(),
            "status": True,
            "message": "New Restaurant has been added.",
            "statusCode": HTTP_201_CREATED
        }), HTTP_201_CREATED
    except ValidationError as err:
        abort(HTTP_422_UNPROCESSABLE_ENTITY, err.messages)


@restaurant.put("/<restaurant_id>")
@app_jwt_required()
@swag_from("./docs/restaurant/update.yaml")
def update(restaurant_id):
    body = request.get_json()
    schema = RestaurantSchema()
    
    valid_id = ObjectId.is_valid(restaurant_id)
    
    if valid_id:
            try:
                restro = Restaurant.objects.get(pk=restaurant_id)
            except VError as error:
                print(error)
                abort(HTTP_404_NOT_FOUND, "Restaurant not found.")
    else:
        abort(HTTP_422_UNPROCESSABLE_ENTITY, "Object Id is invalid.")
    
    try:
        data = schema.load(body)
        update_ok = restro.update(**data)
        restro = Restaurant.objects(id=restaurant_id).first()
        return jsonify({
            "data": restro.object(),
            "status": True,
            "message": "Restaurant has been updated.",
            "statusCode": HTTP_200_OK
        }), HTTP_200_OK
    except ValidationError as err:
        abort(HTTP_422_UNPROCESSABLE_ENTITY, err.messages)