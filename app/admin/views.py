#encoding:utf-8
from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, session, g
from flask.ext.login import login_required, current_user
from ..models import Permission, Role, User, Post, Comment, Message, Category, Star, Webpush
from ..decorators import admin_required, permission_required
from .. import db
from . import admin


@admin.route('/', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(): 
	admins = User.query.filter_by(role_id=2).all()
	return render_template('admin/admin.html',admins=admins)


@admin.route('/admin2user/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin2user(id):
	user = User.query.get_or_404(id)
	user.role = Role.query.filter_by(name='User').first()
	db.session.add(user)
	flash ('已将" '+user.name+' "降为普通用户')
	return redirect(url_for('.edit'))