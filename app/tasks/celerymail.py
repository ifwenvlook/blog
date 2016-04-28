#encoding:utf-8
from .. import celery, mail, create_app, db
from ..models import  User, Post, Webpush

@celery.task
def send_async_email(msg):
    app = create_app('default')
    with app.app_context():
        mail.send(msg)

@celery.task
def send_async_webpush(username,postid):
	app = create_app('default')
	with app.app_context():
	    user = User.query.filter_by(username=username).first()
	    post = Post.query.get(postid)	    
	    followers = user.followers
	    for follower in followers:
	    	if follower.follower != user:	    		
	        	webpush = Webpush(sendto=follower.follower,author=user,post_id=post.id)
	        
