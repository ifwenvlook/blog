from flask import current_app
from app import celery, mail



@celery.task
def send_async_email(msg):
	mail.send(msg)
