from flask import Flask, config, redirect, jsonify, request, abort
from os import environ
from werkzeug.exceptions import HTTPException, InternalServerError
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter, RateLimitExceeded
from flask_jwt_extended import JWTManager
from flask_jwt_extended.exceptions import NoAuthorizationError

from src.database import db
from src.auth import auth
from src.bookmark import bookmark
from src.constants.http_status_codes import HTTP_401_UNAUTHORIZED


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=environ.get('SECRET_KEY'),
            JWT_SECRET_KEY=environ.get('JWT_SECRET')
        )

        app.config["MONGODB_SETTINGS"] = {
            "db": "Boilerplate",
            "host": environ.get('MONGO_DB_URL'),
            "port": 27017,
        }
    else:
        app.config.from_mapping(test_config)

    # cors init
    cors = CORS(app)

    # brypt init
    bcrypt = Bcrypt(app)

    # init db things
    db.app = app
    db.init_app(app)

    # jwt things init
    jwt = JWTManager(app)

    # register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(bookmark)
    # calls when someone hit the route before sending to the methods

    @app.before_request
    def log_request_info():
        app.logger.info('Headers: %s', request.headers)
        app.logger.debug('Body: %s', request.get_data())

        accept_header = request.headers.get("Accept", None)

        if not accept_header == "application/json":
            abort(404, "Direction you're looking for is unavailable.")

    # calls at the end of request fullfill

    @app.after_request
    def after_request(response):
        app.logger.info(response.headers)
        app.logger.debug(response.get_data())

        return response

     # Error Handler method

    @app.errorhandler(HTTPException or RateLimitExceeded or InternalServerError or NoAuthorizationError)
    def handle_exception(e):
        return jsonify({"status": False, "message": e.description, "statusCode": e.code}), e.code

    @jwt.expired_token_loader
    def my_expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"status": False, "message": "Token Expired.", "statusCode": HTTP_401_UNAUTHORIZED}), HTTP_401_UNAUTHORIZED

    return app
