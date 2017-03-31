# coding: utf-8
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import datetime, os, sys
from web.app import login_manager
from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app, request, url_for
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),os.path.pardir))
import app


db = SQLAlchemy(app.app)

class Permission:
    Visitor = 0x01
    Renter = 0x02
    Lanlord = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    type = db.Column(db.Integer, unique=True)
    last_seen = db.Column(db.DateTime(), default=datetime.datetime.utcnow)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions
    def ping(self):
        self.last_seen = datetime.datetime.utcnow()
        db.session.add(self)

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class Area(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Area %s>' % self.name


class Bulletin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dt = db.Column(db.DateTime)
    title = db.Column(db.String(68))
    content = db.Column(db.String(3000))
    valid = db.Integer
    source = db.Column(db.String(68))
    author_id = db.Column(db.ForeignKey(u'users.id'))

    author = db.relationship(u'User')

    def __init__(self, dt, title, content, source, author_id):
        self.dt = dt
        self.title = title
        self.content = content
        self.valid = 1
        self.source = source
        self.author_id = author_id

    def __repr__(self):
        return '<Bulletin %s>' % self.title


class Bulletinimage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bulletin_id = db.Column(db.ForeignKey(u'bulletin.id'))
    file = db.Column(db.String(500))

    bulletin = db.relationship(u'Bulletin', backref = db.backref('bulletinimages', cascade="all, delete-orphan"))

    def __init__(self, bulletin_id, file):
        self.bulletin_id = bulletin_id
        self.file = file

    def __repr__(self):
        return '<Bulletinimage %d,%s>' % (self.bulletin_id, self.file)


class Residential(db.Model):
    __tablename__ = 'residential'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Residential %s>' % self.name


class Mode(db.Model):
    __tablename__ = 'mode'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Mode %s>' % self.name


class Rent(db.Model):
    __tablename__ = 'rent'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))  # 标题
    price = db.Column(db.Integer)  # 价格
    description = db.Column(db.Text)  # 描述
    area_id = db.Column(db.ForeignKey(u'area.id'))  # 区县
    rent_type = db.Column(db.Integer)  # 类型
    mode_id = db.Column(db.ForeignKey(u'mode.id'))  # (整租，单间，合租)
    contacts = db.Column(db.String(20))  # 联系人
    phone_number = db.Column(db.Integer)   # 联系方式
    date = db.Column(db.DateTime)   # 发布日期
    residential_id = db.Column(db.ForeignKey(u'residential.id'))  # 小区名称
    size = db.Column(db.String(20))    # 面积
    address = db.Column(db.String(50))  # 地址
    subway_line = db.Column(db.ForeignKey(u'subway.id'))  # 地铁几号线附近
    decorate_type = db.Column(db.Boolean)  # 装修类型
    author_id = db.Column(db.ForeignKey(u'users.id')) # 发布人
    times  = db.Column(db.Integer) # 访问次数
    # 房屋类型
    residential = db.relationship(u'Residential')
    area = db.relationship(u'Area')
    subway = db.relationship(u'Subway')
    mode = db.relationship(u'Mode')
    author = db.relationship(u'User')

    def __init__(self, area_id, title, price, description, rent_type, mode_id, contacts, phone_number, date,
                 residential_id, size, address, decorate_type, subway_line, author_id, times):
        self.area_id = area_id
        self.title = title
        self.price = price
        self.description = description
        self.rent_type = rent_type
        self.mode_id = mode_id
        self.contacts = contacts
        self.phone_number = phone_number
        self.date = date
        self.residential_id = residential_id
        self.size = size
        self.address = address
        self.decorate_type = decorate_type
        self.subway_line = subway_line
        self.author_id = author_id
        self.times = times

    def __repr__(self):
        return '<Rent %s>' % self.name


class Rentimage(db.Model):
    __tablename__ = 'rentimages'
    id = db.Column(db.Integer, primary_key=True)
    rent_id = db.Column(db.ForeignKey(u'rent.id'))
    file = db.Column(db.String(500))

    rent = db.relationship(u'Rent', backref=db.backref('rentimages', cascade="all, delete-orphan"))

    def __init__(self, rent_id, file):
        self.rent_id = rent_id
        self.file = file

    def __repr__(self):
        return '<Rentimage %d,%s>' % (self.rent_id, self.file)


class Demand(db.Model):
    __tablename__ = 'demand'
    id = db.Column(db.Integer, primary_key=True)
    price_low = db.Column(db.Integer)  # 最低价格
    price_high = db.Column(db.Integer)  # 最高价格
    area_id = db.Column(db.ForeignKey(u'area.id'))  # 区县
    contacts = db.Column(db.String(20))  # 联系人
    phone_number = db.Column(db.Integer)  # 联系方式
    mode_id = db.Column(db.ForeignKey(u'mode.id'))  # (整租，单间，合租)
    decorate_type = db.Column(db.Boolean)  # 装修类型
    subway_line = db.Column(db.ForeignKey(u'subway.id'))  # 地铁几号线附近
    description = db.Column(db.Text)  # 描述
    date = db.Column(db.DateTime)  # 发布日期
    title = db.Column(db.String(50))  # 标题
    author_id = db.Column(db.ForeignKey(u'users.id'))  # 发布人

    area = db.relationship(u'Area')
    subway = db.relationship(u'Subway')
    mode = db.relationship(u'Mode')
    author = db.relationship(u'User')

    def __init__(self, price_low, price_high, area_id, contacts, phone_number, mode_id, decorate_type, subway_line,
                 description, date, title, author_id):
        self.price_high = price_high
        self.price_low = price_low
        self.area_id = area_id
        self.contacts = contacts
        self.phone_number = phone_number
        self.mode_id = mode_id
        self.decorate_type = decorate_type
        self.subway_line = subway_line
        self.description = description
        self.date = date
        self.title = title
        self.author_id = author_id

    def __repr__(self):
        return '<Demand %s>' % self.name


class Subway(db.Model):
    __tablename__ = 'subway'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Subway %s>' % self.name


class Like(db.Model):
    __tablename__ = 'like'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    rent_id = db.Column(db.Integer)

    def __init__(self, user_id, rent_id):
        self.user_id = user_id
        self.rent_id = rent_id