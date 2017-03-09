# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, BooleanField,HiddenField, TextAreaField, SelectField, DecimalField, SelectMultipleField, DateTimeField, BooleanField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, Required, Email, EqualTo
from wtforms import ValidationError
from flask.ext.uploads import UploadSet, IMAGES
from flask.ext.wtf.file import FileField, FileAllowed, FileRequired
from models import User
images = UploadSet('images', IMAGES)


class PageInfo():
    def __init__(self, pagename=""):
       self.pagename = pagename


class RegistrationForm(Form):
    email = StringField(u'电子邮箱', validators=[Required(), Length(1, 64),
                                           Email()])
    username = StringField(u'用户名', validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          'Usernames must have only letters, '
                                          'numbers, dots or underscores')])
    password = PasswordField(u'密码', validators=[Required(), EqualTo('password2', message=u'两次输入必须相同')])
    password2 = PasswordField(u'确认密码', validators=[Required()])
    user_type = SelectField(u'用户类型', validators=[Required()] ,choices=[('0', u'房客'),('1', u'房东')])
    submit = SubmitField(u'注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'该邮箱已被注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u'该用户已被注册')


class LoginForm(Form):
    email = StringField(u'电子邮箱', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField(u'密码', validators=[Required()])
    remember_me = BooleanField(u'保持登录')
    submit = SubmitField(u'登录')


class PasswordResetForm(Form):
    email = StringField(u'电子邮箱', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField(u'新的密码', validators=[
        Required(), EqualTo('password2', message=u'两次密码必须相同')])
    password2 = PasswordField(u'确认密码', validators=[Required()])
    submit = SubmitField(u'重置密码')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError(u'邮箱地址未知')


class PasswordResetRequestForm(Form):
    email = StringField(u'电子邮箱', validators=[Required(), Length(1, 64), Email()])
    submit = SubmitField(u'重置密码')


class SchoolForm(Form):
    id = HiddenField('id')
    name = StringField('学校名称', validators=[Length(min=1, max= 50)]) # 学校名称
    area_id = SelectField(u'所在区县', coerce=int) #区县
    teachdesc = TextAreaField(u'校长及教师情况') #
    address = StringField('地址') #
    schooltype_id = SelectField(u'学校类型', coerce=int) #
    website = StringField('网址') #
    distinguish = TextAreaField(u'教学特色') #
    leisure = TextAreaField(u'课外特色活动') #
    threashold = TextAreaField(u'招生条件及招生地块') #
    partner = StringField('对口学校') #
    artsource = StringField('艺术特长招生情况') # 
    feedesc = StringField('学费标准') #
    longitude = DecimalField('经度', places=4)
    latitude =  DecimalField('纬度', places=4)
    feature_ids =  SelectMultipleField(u'教学特色', coerce=int)
    image = FileField('上传图片', validators= [FileAllowed(['jpg', 'png'], 'Images only!')])


class InstitutionForm(Form):
    id = HiddenField('id')
    name = StringField('品牌名', validators=[Length(min=1, max= 50)]) 
    agespan_id = SelectField(u'招生年龄', coerce=int)
    area_id = SelectField(u'所在区县', coerce=int)
    address = StringField('地址') #
    location = StringField('校区名')
    website = StringField('网址') #
    telephone = StringField('电话')
    feedesc = StringField('学费标准') #
    timeopen = DateTimeField('开业时间', format='%H:%M')
    timeclose = DateTimeField('关门时间', format='%H:%M')
    feetype_id = SelectField('收费类型', coerce=int)
    longitude = DecimalField('经度', places=4)
    latitude =  DecimalField('纬度', places=4)
    #featuredesc = db.Column(db.String(200)) #特色小项描述
    feature_ids =  SelectMultipleField(u'培训方向', coerce=int)
    image = FileField('上传图片', validators= [FileAllowed(['jpg', 'png'], 'Images only!')])


class BulletinForm(Form):
    id = HiddenField('id')
    dt = DateTimeField('发布时间', format = '%Y-%m-%d %H:%M:%S')
    title = StringField('标题')
    content = TextAreaField('详情')
    valid = BooleanField('是否有效')
    source = StringField('来源')
    author =StringField('作者')
    image = FileField('上传图片', validators= [FileAllowed(['jpg', 'png'], 'Images only!')])


class AccountForm(Form):
    id = HiddenField('id')
    dtcreate = DateTimeField('注册时间', format = '%Y-%m-%d %H:%M:%S')
    username = StringField('登录名')
    password = StringField('密码')
    name = StringField('昵称')
    telephone = StringField('注册电话')
    flag_telephone = BooleanField('是否已认证')
    checkcode = StringField('认证码')
    source = StringField('来源')

    def validate_username(self, field):
        if Account.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已存在')