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

from src.auth import app_jwt_required

from src.database import User, Bookmark, BookmarkSchema, UserSchema, db
from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_409_CONFLICT, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN, HTTP_503_SERVICE_UNAVAILABLE


bookmark = Blueprint("bookmark", __name__, url_prefix="/api/v1/bookmark")


@bookmark.get("/")
@app_jwt_required()
def bookmark_list():
    user = User.objects(id=get_jwt_identity()).first()
    # bookmarks = Bookmark.objects(user=get_jwt_identity()).order_by('+createdAt', '-name') #first order by created date and desc by name
    # bookmarks = Bookmark.objects.all().count()

    paginator = Pagination(Bookmark.objects(
        user=get_jwt_identity()).order_by('+createdAt', '-name'), 1, 2)

    # "links": {
    #     "first": "http://upstar.test/api/v1/misc/blog-categories?page=1",
    #     "last": "http://upstar.test/api/v1/misc/blog-categories?page=1",
    #     "prev": null,
    #     "next": null
    # },
    # "meta": {
    #     "current_page": 1,
    #     "from": 1,
    #     "last_page": 1,
    #     "links": [
    #         {
    #             "url": null,
    #             "label": "&laquo; Previous",
    #             "active": false
    #         },
    #         {
    #             "url": "http://upstar.test/api/v1/misc/blog-categories?page=1",
    #             "label": "1",
    #             "active": true
    #         },
    #         {
    #             "url": null,
    #             "label": "Next &raquo;",
    #             "active": false
    #         }
    #     ],
    #     "path": "http://upstar.test/api/v1/misc/blog-categories",
    #     "per_page": 10,
    #     "to": 1,
    #     "total": 1
    # },
    links = {
        "first": "",
        "last": "",
        "prev": "",
        "next": ""
    }

    meta = {
        "currentPage": paginator.page,
        "from": 1,
        "lastPage": 1,
        "links":
            [
                {
                    "url": None,
                    "label": "",
                    "active": False
                },
                {
                    "url": None,
                    "label": "",
                    "active": False
                }
            ],
        "path": environ.get('FLASK_URL') + request.path,
        "per_page": paginator.per_page,
        "to": 1,
        "total": paginator.total
    },

    return jsonify({
        "data": paginator.items,
        "links": links,
        "meta": meta,
        "status": True,
        "message": "",
        "statusCode": HTTP_200_OK
    }), HTTP_200_OK


@bookmark.post("/")
@jwt_required()
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
