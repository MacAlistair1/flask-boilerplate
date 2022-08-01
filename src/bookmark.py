from flask import request, Blueprint, jsonify, abort
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

from src.auth import app_jwt_required

from src.database import User, Bookmark, BookmarkSchema, UserSchema, db
from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_409_CONFLICT, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN, HTTP_503_SERVICE_UNAVAILABLE

from common import paginator_service

bookmark = Blueprint("bookmark", __name__, url_prefix="/api/v1/bookmark")


@bookmark.get("/")
@app_jwt_required()
@swag_from("./docs/bookmark/list.yaml")
def bookmark_list():
    per_page = request.args.get('perPage') if request.args.get(
        'perPage') != None else 10
    current_page = request.args.get('currentPage') if request.args.get(
        'currentPage') != None else 1

    paginator = Pagination(Bookmark.objects(
        user=get_jwt_identity()).order_by('+createdAt', '-name'), int(current_page), int(per_page))
    items = [Bookmark.object(item) for item in paginator.items]
    return paginator_service(paginator, items)


@bookmark.post("/")
@jwt_required()
@swag_from("./docs/bookmark/store.yaml")
def create():
    user = User.objects(id=get_jwt_identity()).first()
    body = request.get_json()
    schema = BookmarkSchema()
    try:
        data = schema.load(body)
        body['user'] = user
        bookmark = Bookmark(**body).save()
        return jsonify({
            "data": bookmark.object(),
            "status": True,
            "message": "New Bookmark has been added.",
            "statusCode": HTTP_201_CREATED
        }), HTTP_201_CREATED
    except ValidationError as err:
        abort(HTTP_422_UNPROCESSABLE_ENTITY, err.messages)
