from flask import Response, request, Blueprint, jsonify, abort
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError
from flask_mongoengine import Pagination
from flasgger import swag_from

from src.auth import app_jwt_required
from src.database import User, Restaurant, RestaurantSchema, db
from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_409_CONFLICT, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN, HTTP_503_SERVICE_UNAVAILABLE

from common import paginator_service, errorResponse
from src.tasks import send_async_email

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

    return ""


@restaurant.route('/send-mail')
def send_mail():
    data = {
        'subject': 'Hello from the other side!',
        'to': ["lamichhaneaj@gmail.com"],
        'body': 'Hey Paul, sending you this email from my Flask app, lmk if it works'
    }
    task = send_async_email.delay(data)
    return "send mail worker started. Task id:"+task.id, 200
