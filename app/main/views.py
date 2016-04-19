#encoding:utf-8
from flask import render_template, redirect, url_for, abort, flash, request,\
    current_app, make_response, session
from flask.ext.login import login_required, current_user
from flask.ext.sqlalchemy import get_debug_queries
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, CommentForm, SendmessageForm
from .. import db
from ..models import Permission, Role, User, Post, Comment,Message,Category
from ..decorators import admin_required, permission_required
from datetime import datetime



@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response


@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'


@main.route('/', methods=['GET', 'POST'])
def index():    
    user = User() 
    message = Message() 
    category = Category()   
    page = request.args.get('page', 1, type=int)
    show_followed = False    
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items[:] #分页显示

    return render_template('index.html',  posts=posts,user=current_user,message=message,category=category,
                            show_followed=show_followed, pagination=pagination,current_time=datetime.utcnow(),hot_post=Post().hotpost())

@main.route('/writepost', methods=['GET', 'POST'])
@login_required
def writepost():    
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        post = Post(body=form.body.data,head=form.head.data,category=Category.query.get(form.category.data),
                    author=current_user._get_current_object())                  
                     #内容、标题、作者、类别
        db.session.add(post)
        flash("博客已发布")
        return redirect(url_for('.index'))
    return render_template('writepost.html',current_time=datetime.utcnow(),form=form,hot_post=Post().hotpost())
        # form1=form1,form2=form2,form3=form3)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts,
                           pagination=pagination,current_time=datetime.utcnow(),hot_post=Post().hotpost() )

#分类路由
@main.route('/category/<int:id>')
def category(id):
    category = Category.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = category.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('category.html',category=category,posts=posts,pagination=pagination,current_time=datetime.utcnow(),hot_post=Post().hotpost())


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form,hot_post=Post().hotpost())


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user,hot_post=Post().hotpost())



@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm() 
    post.visits+=1
    print ("visits+1")
    
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,post=post,sendto=post.author,
            author=current_user._get_current_object())
        db.session.add(comment)
        flash('你的评论已提交.')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // \
            current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    #cookie统计
    # resp = make_response(redirect(url_for('.post',id=post.id))) 
    # reset_last_visit_time = False    
    # if 'last_visit' in request.cookies:
    #     last_visit_time = datetime.fromtimestamp(int(request.cookies.get('last_visit')))
    #     if 0<( datetime.now() - last_visit_time ).seconds< 5:
    #         post.visits=post.visits+1
    #         db.session.add(post)
    #         db.session.commit()
    #         print ("visits+1 aggain")
    # else:
    #     reset_last_visit_time = True

    # if reset_last_visit_time:        
    #     resp.set_cookie('last_visit', str(int(round(float(datetime.now().timestamp())))),max_age=60*60)
    #     resp.set_cookie('visits', '0',max_age=60*60)
    #     post.visits=post.visits+1
    #     db.session.add(post)
    #     db.session.commit()
    #     print ("visits+1")
    #     return resp
    return render_template('post.html', posts=[post], form=form,
                           comments=comments, pagination=pagination,current_time=datetime.utcnow(),hot_post=Post().hotpost() )

@main.route('/post/delete/<int:id>')
def post_delete(id):
    post=Post.query.get_or_404(id)
    db.session.delete(post)
    for comment in post.comments:
        db.session.delete(comment)
    flash('博客以及相关的评论已删除')
    return redirect(url_for('.user', username=post.author.username))



@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        post.head = form.head.data
        #博客内容和标题
        db.session.add(post)
        flash('The post has been updated.')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    form.head.data = post.head
    return render_template('edit_post.html', form=form,current_time=datetime.utcnow(),hot_post=Post().hotpost() )


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash('You are now following %s.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash('You are not following %s anymore.' % username)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows,current_time=datetime.utcnow(),hot_post=Post().hotpost() )


@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows,current_time=datetime.utcnow(),hot_post=Post().hotpost() )


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp

@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)),hot_post=Post().hotpost())


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)),hot_post=Post().hotpost())



@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page,current_time=datetime.utcnow(),hot_post=Post().hotpost() )


@main.route('/shownotice')
@login_required
@permission_required(Permission.COMMENT)
def shownotice():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('shownotice.html', comments=comments,
                           pagination=pagination, page=page,current_time=datetime.utcnow(),hot_post=Post().hotpost() )


@main.route('/shownotice/unconfirmed/<int:id>')
@login_required
@permission_required(Permission.COMMENT)
def shownotice_unconfirmed(id):
    comment = Comment.query.get_or_404(id)
    comment.confirmed = True
    db.session.add(comment)
    return redirect(url_for('.shownotice',
                            page=request.args.get('page', 1, type=int)),hot_post=Post().hotpost())


@main.route('/shownotice/confirmed/<int:id>')
@login_required
@permission_required(Permission.COMMENT)
def shownotice_confirmed(id):
    comment = Comment.query.get_or_404(id)
    comment.confirmed = False
    db.session.add(comment)
    return redirect(url_for('.shownotice',
                            page=request.args.get('page', 1, type=int)),hot_post=Post().hotpost())



@main.route('/usercomments/<username>')
@login_required
@permission_required(Permission.COMMENT)
def usercomments(username):
    user=User.query.filter_by(username=username).first()
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('usercomments.html', comments=comments,user=user,
                           pagination=pagination, page=page,current_time=datetime.utcnow(),hot_post=Post().hotpost() )

@main.route('/usercomments/delete/<int:id>')
@login_required
@permission_required(Permission.COMMENT)
def usercomments_delete(id):
    comment = Comment.query.get_or_404(id)
    db.session.delete(comment)
    flash("评论已删除")
    return redirect(url_for('.usercomments',
                            page=request.args.get('page', 1, type=int)))


@main.route('/sendmessage/<username>', methods=['GET', 'POST'])
@login_required
@permission_required(Permission.COMMENT)
def sendmessage(username):
    user = User.query.filter_by(username=username).first()
    form = SendmessageForm()
    if form.validate_on_submit():
        message = Message(body=form.body.data, \
                    author=current_user,
                    sendto=user)
        db.session.add(message)
        db.session.commit()
        flash('私信发送成功')
        return redirect(url_for('.user', username=username))
        
    return render_template('sendmessage.html', form=form,current_time=datetime.utcnow(),hot_post=Post().hotpost())

@main.route('/showmessage')
@login_required
@permission_required(Permission.COMMENT)
def showmessage():
    page = request.args.get('page', 1, type=int)
    pagination = Message.query.order_by(Message.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    messages = pagination.items
    return render_template('showmessage.html', messages=messages,
                           pagination=pagination, page=page,current_time=datetime.utcnow() ,hot_post=Post().hotpost())


@main.route('/showmessage/unconfirmed/<int:id>')
@login_required
@permission_required(Permission.COMMENT)
def showmessage_unconfirmed(id):
    message = Message.query.get_or_404(id)
    message.confirmed = True
    db.session.add(message)
    return redirect(url_for('.showmessage',
                            page=request.args.get('page', 1, type=int)))


@main.route('/showmessage/confirmed/<int:id>')
@login_required
@permission_required(Permission.COMMENT)
def showmessage_confirmed(id):
    message = Message.query.get_or_404(id)
    message.confirmed = False
    db.session.add(message)
    return redirect(url_for('.showmessage',
                            page=request.args.get('page', 1, type=int)))


@main.route('/showmessage/delete/<int:id>')
@login_required
@permission_required(Permission.COMMENT)
def message_delete(id):
    message = Message.query.get_or_404(id)    
    db.session.delete(message)
    flash('私信删除成功')
    return redirect(url_for('.showmessage',
                            page=request.args.get('page', 1, type=int)))


@main.route('/firstpage', methods=['GET', 'POST'])
def firstpage():
    return render_template('aboutme.html',current_time=datetime.utcnow(),hot_post=Post().hotpost())



# @main.route('/firstpage', methods=['GET', 'POST'])
# def firstpage():
#     return render_template('firstpage.html')

# @main.route('/firstpage', methods=['GET', 'POST'])
# def firstpage():
#     return render_template('first1.html')
