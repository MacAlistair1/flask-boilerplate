from flask import Response, request, Blueprint, jsonify, abort
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity, verify_jwt_in_request, get_jwt
from os import environ
from marshmallow import ValidationError
import string
import random
import requests
from flask_jwt_extended.exceptions import NoAuthorizationError, InvalidHeaderError
from functools import wraps
from flask_mongoengine import Pagination
from flasgger import swag_from
import bson.json_util as json_util

from src.auth import app_jwt_required

from src.database import User, Restaurant, RestaurantSchema, db
from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_409_CONFLICT, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN, HTTP_503_SERVICE_UNAVAILABLE

from common import paginator_service

restaurant = Blueprint("restaurant", __name__, url_prefix="/api/v1/restaurant")


@restaurant.get("/")
@app_jwt_required()
def restaurant_list():
    per_page = request.args.get('perPage') if request.args.get(
        'perPage') != None else 10
    current_page = request.args.get('currentPage') if request.args.get(
        'currentPage') != None else 1

# 27.719622795070237, 85.30442831534448

    agg = [{"$geoNear": {"near": [85.30442831534448, 27.719622795070237],
                         "distanceField":"distance", "maxDistance":3, "spherical":True}}]

    data = Restaurant.objects().aggregate(*agg)
    
    items = []

    for doc in data:
        return Response(Restaurant.object(json_util.dumps(doc)), mimetype="application/json")

    return ""
    # paginator = Pagination(data, int(current_page), int(per_page))
    # items = [Restaurant.object(item) for item in paginator.items]
    # return paginator_service(paginator, items)


@ restaurant.post("/")
@ app_jwt_required()
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

    return ""
