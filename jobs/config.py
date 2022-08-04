#FLASK
SECRET_KEY="secure_key"
FLASK_ENV="development"
FLASK_APP="app"
FLASK_APP_NAME="Boilerplate"
SERVER_NAME="127.0.0.1:5001"

# Flask-Mail
MAIL_SERVER = 'smtp.mailtrap.io'
MAIL_PORT = 2525
MAIL_USE_TLS = True
MAIL_USERNAME = '3e8f4d52a62a2a'
MAIL_PASSWORD = '5badb2a5c8bf03'
MAIL_DEFAULT_SENDER='info@boilerplate.com'


#celery redis
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_BACKEND_URL = 'redis://localhost:6379/0'