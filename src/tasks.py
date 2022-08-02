from os import environ

from celery import Celery
from flask_mail import Message
import src


mail = src.create_app



celery = Celery(__name__)
celery.conf.broker_url = environ.get(
    "CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = environ.get(
    "CELERY_RESULT_BACKEND", "redis://localhost:6379")


@celery.task(name="send_async_email")
def send_async_email(data):
    msg = Message(data['subject'],
                  sender=environ.get("MAIL_DEFAULT_SENDER"),
                  recipients=data['to'])
    msg.body = data['body']
    mail.send(msg)
    return True
