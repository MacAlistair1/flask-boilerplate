#FLASK
SECRET_KEY="secure_key"
FLASK_ENV="development"
FLASK_APP="app"

# Flask-Mail
MAIL_SERVER = 'smtp.mailtrap.io'
MAIL_PORT = 2525
MAIL_USE_TLS = True
MAIL_USERNAME = '3e8f4d52a62a2a'
MAIL_PASSWORD = '5badb2a5c8bf03'


#celery redis
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_BACKEND_URL = 'redis://localhost:6379/0'