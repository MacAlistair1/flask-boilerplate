from flask import Flask, jsonify, request, abort
from os import environ
from werkzeug.exceptions import HTTPException, InternalServerError, BadRequest, NotFound, MethodNotAllowed
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter, RateLimitExceeded
from flask_jwt_extended import JWTManager
from flask_jwt_extended.exceptions import NoAuthorizationError
import logging
from flasgger import Swagger
from flask_mail import Mail, Message
import requests

from src.database import db
from src.auth import auth
from src.bookmark import bookmark
from src.restaurant import restaurant
from src.constants.http_status_codes import HTTP_401_UNAUTHORIZED
from src.config.swagger import template, swagger_config
from common import errorResponse

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=environ.get('SECRET_KEY'),
            JWT_SECRET_KEY=environ.get('JWT_SECRET'),
            SWAGGER={
                'title': environ.get('FLASK_APP_NAME') if environ.get('FLASK_APP_NAME') != None else "Boilerplate Api",
                'uiversion': 3
            }
        )

        app.config["MONGODB_SETTINGS"] = {
            "db": "Boilerplate",
            "host": environ.get('MONGO_DB_URL'),
            "port": 27017,
        }

        app.config['MAIL_SERVER'] = environ.get('MAIL_SERVER')
        app.config['MAIL_PORT'] = environ.get('MAIL_PORT')
        app.config['MAIL_USERNAME'] = environ.get('MAIL_USERNAME')
        app.config['MAIL_PASSWORD'] = environ.get('MAIL_PASSWORD')
        app.config['MAIL_USE_TLS'] = bool(environ.get('MAIL_USE_TLS'))
        app.config['MAIL_USE_SSL'] = False

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
    app.register_blueprint(restaurant)

    # swagger init
    Swagger(app, config=swagger_config, template=template)

    # mail init
    mail = Mail(app)

    # For Logging on Debug Mode
    logging.basicConfig(filename='user.log', level=logging.DEBUG,
                        format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

    # calls when someone hit the route before sending to the methods

    @app.before_request
    def log_request_info():

        accept_header = request.headers.get("Accept", None)

        # store logs only if accept header is json
        if accept_header == "application/json":
            app.logger.info('Headers: %s', request.headers)
            app.logger.debug('Body: %s', request.get_data())

        # d nothing for swagger end points
        if request.path == "/apispec.json" or request.path == "/apidocs" or "flasgger_static" in request.path or request.path == "/" or request.path == "/echo":
            pass
        else:
            # return 404 if the accept header is not json except for the swagger json path
            if not accept_header == "application/json":
                abort(404, "Direction you're looking for is unavailable.")

        # calls at the end of request fullfill

    @app.after_request
    def after_request(response):
        accept_header = request.headers.get("Accept", None)
        # store logs only if accept header is json
        if accept_header == "application/json":
            app.logger.info(response.headers)
            app.logger.debug(response.get_data())

        return response

     # Error Handler method

    @app.errorhandler(HTTPException or RateLimitExceeded or InternalServerError or NoAuthorizationError or BadRequest or MethodNotAllowed or NotFound)
    def handle_exception(e):
        return jsonify({"status": False, "message": e.description, "statusCode": e.code}), e.code

    @jwt.expired_token_loader
    def my_expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"status": False, "message": "Token Expired.", "statusCode": HTTP_401_UNAUTHORIZED}), HTTP_401_UNAUTHORIZED

    @app.get('/')
    def send_mail():
        
        try:
            url = environ.get("JOBS_BASE_URL")+"/send-mail"
            
            data = {
            "subject" : "Mail Subject",
            "body": "Hello Flask message sent from Flask-Mail",
            "recipients": ["lamichhaneaj@gmail.com", "lamichhaneaj1@gmail.com", 
                           "lamichhaneaj2@gmail.com", "lamichhaneaj3@gmail.com", 
                           "lamichhaneaj4@gmail.com", "lamichhaneaj5@gmail.com", 
                           "lamichhaneaj6@gmail.com", "lamichhaneaj7@gmail.com", 
                           "lamichhaneaj8@gmail.com", "lamichhaneaj9@gmail.com", 
                           "lamichhaneaj10@gmail.com", "lamichhaneaj11@gmail.com"],
            }
            
            headers = {
                'Content-Type': "application/json",
                'Accept': "application/json",
            }
            response = requests.request("POST", url, headers=headers, json=data)
            print(response)
            
            return "Message Sent", 200
            

        except Exception as e:
            return errorResponse("Connection Failure!!", 503)

    return app
