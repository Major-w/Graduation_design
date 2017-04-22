import sys, os
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask import Flask, request
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config


reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))


bootstrap = Bootstrap()
mail = Mail()
db = SQLAlchemy()
moment = Moment()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
app = Flask(__name__)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    return app

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+pg8000://postgres:123123@localhost/graduation'
app.config['WTF_CSRF_ENABLED'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'hard to guess string'
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')
app.config['FLASKY_MAIL_SENDER'] = '471397033@qq.com'
app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['MAIL_USERNAME'] = '471397033'
app.config['MAIL_PASSWORD'] = 'hjyelcgkrdhbbiig'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['FLASKY_COMMENTS_PER_PAGE'] = 10
app.config['FLASKY_SLOW_DB_QUERY_TIME'] = 0.5

bootstrap.init_app(app)
mail.init_app(app)
moment = Moment(app)
api = Api(app)
db.init_app(app)
login_manager.init_app(app)
app.debug = True

