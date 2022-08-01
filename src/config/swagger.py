from os import environ


template = {
    "swagger": "2.0",
    "info": {
        "title": environ.get('FLASK_APP_NAME') + " Api" if environ.get('FLASK_APP_NAME') != None else "Boilerplate Api",
        "description": "API for " + environ.get('FLASK_APP_NAME') if environ.get('FLASK_APP_NAME') != None else "Boilerplate",
        "contact": {
            "responsibleOrganization": "Eydean Inc.",
            "responsibleDeveloper": "Jeeven Lamichhane",
            "email": "lamichhaneaj@gmail.com",
            "url": "https://jeevenlamichhane.com.np",
        },
        "termsOfService": "https://jeevenlamichhane.com.np",
        "version": "1.0"
    },
    "basePath": "/api/v1",  # base bash for blueprint registration
    "schemes": [
        "http",
        "https"
    ],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
        }
    },
}

swagger_config = {
    "headers": [
    ],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/"
}
