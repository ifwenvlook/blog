#encoding:utf-8
from .. import celery, mail, create_app, db
from ..models import  User, Post, Webpush

@celery.task
def send_async_email(msg):
    app = create_app('default')
    with app.app_context():
        mail.send(msg)

@celery.task
def send_async_webpush(username,post):
	app = create_app('default')
	with app.app_context():
	    user = User.query.filter_by(username=username).first()
	    post = post
	    followers = user.followers
	    for follower in followers:
	        webpush = Webpush(head=post.head,body=post.body,sendto=follower.follower)
	        
