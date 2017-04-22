# coding:utf-8
import unittest
import os
basedir = os.path.abspath(os.path.dirname(__file__))
from flask import current_app,url_for
from web.app import app, db
from DB import orm
app.config['WTF_CSRF_ENABLED'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+pg8000://postgres:rootroot@localhost/Graduation'

class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(use_cookies=True)
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        try:
            result = orm.User.query.filter_by(email='471398033@qq.com').one()
            orm.db.session.delete(result)
            orm.db.session.commit()
        except:
            pass

    def test_home_page(self):
        response = self.client.get(url_for('rootDir'))
        self.assertTrue(response.status_code == 302)

    def test_register_and_login(self):
        """
        测试注册和登陆
        :return:
        """
        # 注册
        response = self.client.post(url_for('register'), data={
            'email': '471398033@qq.com',
            'username': 'jikai01',
            'password': '123',
            'password2': '123',
            'user_type': '0'
        })
        self.assertTrue(response.status_code == 302)    # 测试注册成功是否跳转

        # 登陆
        response = self.client.post(url_for('login'), data={
            'email': '471398033@qq.com',
            'password': '123'
        }, follow_redirects=True)
        self.assertTrue(b'所有出租信息' in response.data)    # 测试登陆成功是否跳转

        # 激活账户
        user = orm.User.query.filter_by(email='471398033@qq.com').first()
        token = user.generate_confirmation_token()
        response = self.client.get(url_for('confirm', token=token, _external=True),
                                   follow_redirects=True)
        self.assertTrue(b'所有出租信息' in response.data)

        # 忘记密码
        token = user.generate_confirmation_token()
        response = self.client.post(url_for('password_reset', token=token, _external=True),data={
            'email': '471398033@qq.com',
            'password': '12345',
            'password2': '12345'
        })
        self.assertTrue(response.status_code == 302)

        # 注销
        response = self.client.get(url_for('logout'), follow_redirects=True)
        self.assertTrue(b'您已经退出登录' in response.data)

        # 更换昵称
        response = self.client.post(url_for('change_username'), data={
            'username': 'test01'
        })
        self.assertTrue(response.status_code == 302)    # 测试是否跳转

        # 更改密码
        response = self.client.post(url_for('change_password'), data={
            'old_password': '12345',
            'password': '1234',
            'password2': '1234'
        })
        self.assertTrue(response.status_code == 302)  # 测试是否跳转

