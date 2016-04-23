#encoding:utf-8
from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField,\
    SubmitField,FieldList
from wtforms.validators import Required, Length, Email, Regexp,AnyOf
from wtforms import ValidationError
from flask.ext.pagedown.fields import PageDownField
from ..models import Role, User, Message, Category



class SendmessageForm(Form):
    body = StringField('私信内容', validators=[Length(0, 256)])
    submit = SubmitField('发送')


class NameForm(Form):
    name = StringField('你的名字', validators=[Required()])
    submit = SubmitField('提交')


class EditProfileForm(Form):
    name = StringField('姓名', validators=[Length(0, 64)])
    location = StringField('地址', validators=[Length(0, 64)])
    about_me = TextAreaField('关于我')
    submit = SubmitField('提交')

class PostForm(Form): 
    category = SelectField('文章类别', coerce=int)  
    head = StringField('标题', validators=[Required(), Length(1, 25)])    
    body = PageDownField("正文", validators=[Required()])    
    submit = SubmitField('发布')
    

    def __init__(self, *args, **kwargs): #定义下拉选择表
        super(PostForm,self).__init__(*args, **kwargs)
        self.category.choices = [(category.id, category.name)
                             for category in Category.query.order_by(Category.name).all()]


class EditProfileAdminForm(Form):
    email = StringField('电子邮箱(Email)', validators=[Required(), Length(1, 64),
                                             Email()])
    username = StringField('用户名', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('姓名', validators=[Length(0, 64)])
    location = StringField('地址', validators=[Length(0, 64)])
    about_me = TextAreaField('关于我')
    submit = SubmitField('提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email已经被使用.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在')

class CommentForm(Form):
    body = StringField('输入你的评论', validators=[Required()])
    submit = SubmitField('提交')


class SearchForm(Form):
    search = StringField('search', validators = [Required()])
