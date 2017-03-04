# coding: utf-8
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import datetime, os, sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),os.path.pardir))
import app


db = SQLAlchemy(app.app)


class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    password = db.Column(db.String(255))
    name = db.Column(db.String(20))
    telephone = db.Column(db.String(50), unique=True)
    role = db.Column(db.Integer)
    flag_telephone = db.Column(db.Integer)
    checkcode = db.Column(db.String(50))
    source = db.Column(db.String(20))
    dtcreate = db.Column(db.DateTime)

    def __init__(self, username=None, password=None, name=None, telephone=None, role=None, flag_telephone=None, checkcode=None, source=None, dtcreate=None):
        self.username = username
        self.password = password
        self.name = name
        self.telephone = telephone
        self.role = role
        self.flag_telephone = flag_telephone
        self.checkcode = checkcode
        self.source = source
        self.dtcreate = dtcreate

    def __repr__(self):
        return '<Account %s>' % self.username


class Test(db.Model):
    user = db.Column(db.String(50), primary_key=True)
    tt = db.Column(db.DateTime())

    def __init__(self, user):
        self.user = user

    def __repr__(self):
        return '<Test %s>' % self.user


class Advert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    website = db.Column(db.String(200))
    image_file = db.Column(db.String(200))

    def __init__(self, title, website, image_file):
        self.title = title
        self.website = website
        self.image_file = image_file

    def __repr__(self):
        return '<Advert %s>' % self.title


class Agespan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(50, collation='utf8_bin'))
    fromage = db.Column(db.Integer)
    toage = db.Column(db.Integer)

    def __init__(self, name, fromage, toage):
        self.name = name
        self.fromage = fromage
        self.toage = toage

    def __repr__(self):
        return '<Agespan %s>' % self.name


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
    author = db.Column(db.String(68))

    def __init__(self, dt, title, content, source, author):
        self.dt = dt
        self.title = title
        self.content = content
        self.valid = 1
        self.source = source
        self.author = author

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



class Feature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Feature %s>' % self.name


class Feetype(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Feetype %s>' % self.name


class Institution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100)) # 品牌名
    agespan_id = db.Column(db.ForeignKey(u'agespan.id')) #招生年龄
    area_id = db.Column(db.ForeignKey(u'area.id')) #区县
    address = db.Column(db.String(100)) #校区地址
    location = db.Column(db.String(100)) # 校区名
    website = db.Column(db.String(100)) #网址
    telephone = db.Column(db.String(50)) #电话
    feedesc = db.Column(db.String(100)) # 学费标准
    timeopen = db.Column(db.DateTime) #开业时间
    timeclose = db.Column(db.DateTime) #关门时间
    feetype_id = db.Column(db.ForeignKey(u'feetype.id'))
    longitude = db.Column(db.Float) #经度
    latitude = db.Column(db.Float)  #纬度
    featuredesc = db.Column(db.String(200)) #特色小项描述

    feetype = db.relationship(u'Feetype')
    area = db.relationship(u'Area')
    agespan = db.relationship(u'Agespan')

    def __init__(self, name, agespan_id, area_id, address, location, website, telephone, feedesc, timeopen, timeclose, feetype_id, longitude, latitude, featuredesc):
        self.name = name
        self.agespan_id = agespan_id
        self.area_id = area_id
        self.address = address
        self.location = location
        self.website = website
        self.telephone = telephone
        self.feedesc = feedesc
        self.timeopen = timeopen
        self.timeclose = timeclose
        self.feetype_id = feetype_id
        self.longitude = longitude
        self.latitude = latitude
        self.featuredesc = featuredesc

    def __repr__(self):
        return '<Institution %s>' % self.name


class InstitutionFeature(db.Model):
    institution_id = db.Column(db.ForeignKey(u'institution.id'), primary_key=True)
    feature_id = db.Column(db.ForeignKey(u'feature.id'), primary_key=True)

    institution = db.relationship(u'Institution', backref = db.backref('institutionfeatures', cascade="all, delete-orphan"))
    feature = db.relationship(u'Feature')

    def __init__(self, institution_id, feature_id):
        self.institution_id = institution_id
        self.feature_id = feature_id

    def __repr__(self):
        return '<InstitutionFeature %s>' % self.name


class Institutionimage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    institution_id = db.Column(db.ForeignKey(u'institution.id'))
    file = db.Column(db.String(500))

    institution = db.relationship(u'Institution', backref = db.backref('institutionimages', cascade="all, delete-orphan"))

    def __init__(self, institution_id, file):
        self.institution_id = institution_id
        self.file = file

    def __repr__(self):
        return '<Institutionimage %d,%s>' % (self.institution_id, self.file)


class School(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100)) # 学校名称
    area_id = db.Column(db.ForeignKey(u'area.id')) #区县
    teachdesc = db.Column(db.Text) #校长及教师情况
    address = db.Column(db.String(100)) #地址
    schooltype_id = db.Column(db.ForeignKey(u'schooltype.id')) #学校性质
    website = db.Column(db.String(100)) #网址
    distinguish = db.Column(db.Text) #教学特色
    leisure = db.Column(db.String(1000)) #课外特色活动
    threashold = db.Column(db.String(1000)) #招生条件及招生地块
    partner = db.Column(db.String(100)) #对口学校
    artsource = db.Column(db.String(1000)) # 艺术特长招生数量
    feedesc = db.Column(db.String(100)) #学费标准
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)


    schooltype = db.relationship(u'Schooltype')
    area = db.relationship(u'Area')


    def __init__(self, name, area_id, teachdesc, address, schooltype_id, website, distinguish, leisure, threashold, partner, artsource, feedesc, longitude, latitude):
        self.name = name
        self.area_id = area_id
        self.teachdesc = teachdesc
        self.address = address
        self.schooltype_id = schooltype_id
        self.website = website
        self.distinguish = distinguish
        self.leisure = leisure
        self.threashold = threashold
        self.partner = partner
        self.artsource = artsource
        self.feedesc = feedesc
        self.longitude = longitude
        self.latitude = latitude


    def __repr__(self):
        return '<School %s>' % self.name



class SchoolFeature(db.Model):
    school_id = db.Column(db.ForeignKey(u'school.id'), primary_key=True)
    feature_id = db.Column(db.ForeignKey(u'feature.id'), primary_key=True)

    school = db.relationship(u'School', backref = db.backref('schoolfeatures', cascade="all, delete-orphan"))
    feature = db.relationship(u'Feature')

    def __init__(self, school_id, feature_id):
        self.school_id = school_id
        self.feature_id = feature_id

    def __repr__(self):
        return '<SchoolFeature %d,%d>' % (self.school_id, self.feature_id)


class Schoolimage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.ForeignKey(u'school.id'))
    file = db.Column(db.String(500))

    school = db.relationship(u'School', backref = db.backref('schoolimages', cascade="all, delete-orphan"))

    def __init__(self, school_id, file):
        self.school_id = school_id
        self.file = file

    def __repr__(self):
        return '<Schoolimage %d,%s>' % (self.school_id, self.file)


class Schooltype(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Schooltype %s>' % self.name


class Terminal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.ForeignKey(u'account.id'))
    os = db.Column(db.String(20))
    code = db.Column(db.String(255))

    account = db.relationship(u'Account', backref = db.backref('terminals'))

    def __init__(self, account_id, os=None, code=None):
        self.account_id = account_id
        self.os = os
        self.code = code

    def __repr__(self):
        return '<Terminal %d,%d,%s>' % (self.account_id, self.type, self.code)



