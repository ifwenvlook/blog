#encoding:utf-8
from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, session, g
from flask.ext.login import login_required, current_user
from ..models import Permission, Role, User, Post, Comment, Message, Category, Star, Webpush
from ..decorators import admin_required, permission_required
from .. import db
from . import admin
from .forms import AddadminForm, AdduserForm, AddcategoryForm


@admin.route('/', methods=['GET', 'POST'])
@login_required
def edit(): 
	page = request.args.get('page', 1, type=int)
	pagination = User.query.filter_by(role_id=2).order_by(User.member_since.desc()).paginate(
		page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
		error_out=False)
	admins = pagination.items
	return render_template('admin/edit.html',admins=admins,pagination=pagination, page=page)


@admin.route('/admin2user/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin2user(id):
	user = User.query.get_or_404(id)
	user.role = Role.query.filter_by(name='User').first()
	db.session.add(user)
	flash ('已将" '+user.username+' "降为普通用户')
	return redirect(url_for('.edit'))

@admin.route('/addadmin', methods=['GET', 'POST'])
@login_required
@admin_required
def addadmin():
	form = AddadminForm()	
	if form.validate_on_submit():
		user = User(email=form.username.data+'@vlblog.com',
					username=form.username.data,
					password=form.password.data,
					confirmed=True,
					role=Role.query.filter_by(permissions=0xff).first())
		db.session.add(user)
		db.session.commit()
		flash('已添加" '+user.username+' "为管理员')
		return redirect(url_for('.edit'))
	return render_template('admin/addadmin.html',form=form)


@admin.route('/edituser', methods=['GET', 'POST'])
@login_required
@admin_required
def edituser():	
	page = request.args.get('page', 1, type=int)
	pagination = User.query.order_by(User.member_since.desc()).paginate(
		page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
		error_out=False)
	users = pagination.items
	return render_template('admin/edituser.html',users=users,pagination=pagination, page=page)

@admin.route('/deleteuser/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def deleteuser(id):
	user = User.query.get_or_404(id)

	posts = user.posts
	for post in posts:
		db.session.delete(post)
	comments = user.comments
	for comment in comments:
		db.session.delete(comment)
	messages = user.messages
	for message in messages:
		db.session.delete(message)
	webpushs = user.webpushs
	for webpush in webpushs:
		db.session.delete(webpush)

	db.session.delete(user)
	flash ('已将和" '+user.username+' "相关的内容删除')
	return redirect(url_for('.edituser'))

@admin.route('/adduser', methods=['GET', 'POST'])
@login_required
@admin_required
def adduser():
	form = AdduserForm()	
	if form.validate_on_submit():
		user = User(email=form.email.data,
					username=form.username.data,
					password=form.password.data,
					confirmed=True)
		db.session.add(user)
		db.session.commit()
		flash('已添加" '+user.username+' "为普通用户')
		return redirect(url_for('.edituser'))
	return render_template('admin/adduser.html',form=form)

@admin.route('/editpost', methods=['GET', 'POST'])
@login_required
@admin_required
def editpost():	
	page = request.args.get('page', 1, type=int)
	pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
		page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
		error_out=False)
	posts = pagination.items
	return render_template('admin/editpost.html',posts=posts,pagination=pagination, page=page)

@admin.route('/post/delete/<int:id>')
@login_required
@admin_required
def deletepost(id):
    post=Post.query.get_or_404(id)
    db.session.delete(post)
    for comment in post.comments:
        db.session.delete(comment)
    for webpush in post.webpushs:
        db.session.delete(webpush)
    flash('博客以及相关的评论、推送已删除')
    return redirect(url_for('.editpost'))

@admin.route('/editcategory', methods=['GET', 'POST'])
@login_required
@admin_required
def editcategory():
	categorys = Category.query.order_by(Category.id).all()
	return render_template('admin/editcategory.html',categorys=categorys)

@admin.route('/addcategory', methods=['GET', 'POST'])
@login_required
@admin_required
def addcategory():
	form = AddcategoryForm()
	if form.validate_on_submit():
		category = Category(name=form.name.data)
		db.session.add(category)
		db.session.commit()
		flash('已添加" '+category.name+' "为新的分类')
		return redirect(url_for('.editcategory'))
	return render_template('admin/addcategory.html',form=form)



@admin.route('/editcomment')
@login_required
@admin_required
def editcomment():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('admin/editcomment.html', comments=comments,
                           pagination=pagination, page=page,   )


@admin.route('/deletecomment/<int:id>')
@login_required
@admin_required
def deletecomment_enable(id):
    comment = Comment.query.get_or_404(id)    
    db.session.delete(comment)
    return redirect(url_for('.editcomment',
                            page=request.args.get('page', 1, type=int)), )   

@admin.route('/editcomment/enable/<int:id>')
@login_required
@admin_required
def editcomment_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.editcomment',
                            page=request.args.get('page', 1, type=int)), )


@admin.route('/editcomment/disable/<int:id>')
@login_required
@admin_required
def editcomment_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.editcomment',
                            page=request.args.get('page', 1, type=int)), )



