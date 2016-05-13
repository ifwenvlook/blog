from .models import  User
from . import db

def deletenone():
	noneuser=User.query.filter_by(username=None).all()
	for user in noneuser:
		db.session.delete(user)
	db.session.commit()
