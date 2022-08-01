
from flask import Blueprint, request, jsonify, abort
from werkzeug.security import check_password_hash, generate_password_hash
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity, verify_jwt_in_request, get_jwt
from os import environ
from marshmallow import ValidationError
import string
import random
import requests
from flask_jwt_extended.exceptions import NoAuthorizationError, InvalidHeaderError
from functools import wraps
from flasgger import swag_from

from src.database import User, UserSchema, VerifyOtpSchema, LoginSchema, db
from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_409_CONFLICT, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN, HTTP_503_SERVICE_UNAVAILABLE


auth = Blueprint("auth", __name__, url_prefix='/api/v1/auth')

# Register Route


@auth.post('/register')
@swag_from('./docs/auth/register.yaml')
def register():
    body = request.get_json()
    register_schema = UserSchema()
    try:
        data = register_schema.load(body)

        user_exist = User.objects(phone=body['phone']).first()

        if user_exist:
            abort(
                HTTP_409_CONFLICT, "User already exist with given phone number.")
        else:
            data['password'] = generate_password_hash(body['password'])
            data['otp'] = "".join(random.choices(string.digits, k=6))
            user = User(**data).save()

            # send otp after user store
            send_otp(user=user)

            access_token = create_access_token(identity=str(user.pk))
            refresh_token = create_refresh_token(identity=str(user.pk))

            return jsonify({
                "data": user.user_profile(access_token, refresh_token),
                "status": True,
                "message": "Registered Successfully.Please check your inbox to verify otp.",
                "statusCode": HTTP_201_CREATED
            }), HTTP_201_CREATED
    except ValidationError as err:
        abort(HTTP_422_UNPROCESSABLE_ENTITY, err.messages)


# Login Route
@auth.post('/login')
@swag_from('./docs/auth/login.yaml')
def login():
    body = request.get_json()
    login_schema = LoginSchema()
    try:
        data = login_schema.load(body)

        user_exist = User.objects(
            countryCode=body['countryCode'], phone=body['phone']).first()

        if not user_exist:
            abort(
                HTTP_404_NOT_FOUND, "Phone number is not found in our records.")
        else:
            if not user_exist.verified:
                abort(
                    HTTP_403_FORBIDDEN, "Phone number is unverified.")

            password_match = check_password_hash(
                user_exist.password, body['password'])

            if password_match:
                access_token = create_access_token(identity=str(user_exist.pk))
                refresh_token = create_refresh_token(
                    identity=str(user_exist.pk))

                return jsonify({
                    "data": user_exist.user_profile(access_token, refresh_token),
                    "status": True,
                    "message": "Login Successfully.",
                    "statusCode": HTTP_200_OK
                }), HTTP_200_OK
            else:
                abort(
                    HTTP_404_NOT_FOUND, "These credentials do not match our records.")

    except ValidationError as err:
        abort(HTTP_422_UNPROCESSABLE_ENTITY, err.messages)


# verify otp
@auth.post('/verify-otp')
@swag_from('./docs/auth/verify_otp.yaml')
def verify_otp():
    body = request.get_json()
    otp_schema = VerifyOtpSchema()
    try:
        data = otp_schema.load(body)

        user_exist = User.objects(
            countryCode=body['countryCode'], phone=body['phone'], otp=body['otp']).first()
        if user_exist:
            user_exist.otp = None
            user_exist.verified = True
            user_exist.save()

            return jsonify({
                "status": True,
                "message": "User has been verified Successfully.",
                "statusCode": HTTP_200_OK
            }), HTTP_200_OK
        else:
            abort(404, "Otp or Phone is not valid.")

    except ValidationError as err:
        abort(HTTP_422_UNPROCESSABLE_ENTITY, err.messages)


# custom decorator for authentication, verify token in header else raise error
def app_jwt_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                return fn(*args, **kwargs)
            except NoAuthorizationError as err:
                abort(401, "Unauthorized.")

        return decorator

    return wrapper


# get the user profile
@auth.get("/my-profile")
@app_jwt_required()
@swag_from('./docs/auth/user_profile.yaml')
def me():
    user_id = get_jwt_identity()
    user = User.objects(id=user_id).first()
    return jsonify({
        "data": user.user_profile(),
        "status": True,
        "message": "",
        "statusCode": HTTP_200_OK
    }), HTTP_200_OK


# generate  new access token using refresh token sent in login
@auth.get('/token/refresh')
@jwt_required(refresh=True)
def refresh_users_token():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({
        "data": {"accessToken": access_token},
        "status": True,
        "message": "Token Refreshed.",
        "statusCode": HTTP_200_OK
    }), HTTP_200_OK


# send otp
def send_otp(user):
    try:
        url = environ.get('SMS_URI')
        payload = {
            "mobile_number": user.phone,
            "message": "<#> Hello " + user.format_name() +
            ",\n"+"Welcome to "+environ.get("FLASK_APP_NAME") +
            ".\nPlease use OTP "+user.otp+" to verify your account, it will be valid for 15 minutes.\nThank You!\n" +
            environ.get("FLASK_APP_NAME"),
            "is_otp": 1
        }
        headers = {
            'apikey': environ.get('SMS_TOKEN')
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        print(response)

    except Exception as err:
        abort(HTTP_503_SERVICE_UNAVAILABLE, err.messages)
