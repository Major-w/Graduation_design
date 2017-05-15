# coding:utf-8
import unittest
import os
from flask import current_app,url_for
from flask_login import current_user
from web.app import app, db
from DB import orm
app.config['WTF_CSRF_ENABLED'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+pg8000://postgres:123123@localhost/graduation'


class GraduationRentTest(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(use_cookies=True)
        db.create_all()
        test_user = orm.User(email='123456789@qq.com', username='testuser', password='123', role_id=3, confirmed=True)
        orm.db.session.add(test_user)
        try:
            orm.db.session.commit()
        except:
            orm.db.session.rollback()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        try:
            result = orm.User.query.filter_by(email='123456789@qq.com').one()
            rents= orm.Rent.query.filter_by(author_id=result.id).all()
            for rent in rents:
                orm.db.session.delete(rent)
            orm.db.session.commit()
        except:
            pass
        try:
            result = orm.User.query.filter_by(email='123456789@qq.com').one()
            orm.db.session.delete(result)
            orm.db.session.commit()
        except:
            pass

    def test_rent(self):
        response = self.client.post(url_for('login'), data={
            'email': '123456789@qq.com',
            'password': '123'
        }, follow_redirects=True)

        # 新建出租信息
        response = self.client.post(url_for('view_rent'), data={
            'contacts': 'test',
            'phone_number': 123456,
            'area_id': 2,
            'mode_id': 1,
            'decorate_type': '0',
            'subway_line': 2,
            'price': 1000,
            'description': 'xxxxxx',
            'title': 'test',
            'rent_type': '0',
            'residential_id': 1,
            'size': 20,
            'address': 'test_address',
            'decorate_type': '0'
        })
        user_id = orm.User.query.filter_by(email='123456789@qq.com').one().id
        rent = orm.Rent.query.filter_by(author_id=user_id).one()
        self.assertEqual(rent.title, 'test')

        # 我的发布(删除)
        response = self.client.get(url_for('my_rent_publish', delete_rent_id=rent.id))
        rents = orm.Rent.query.filter_by(author_id=user_id, id=rent.id).all()
        self.assertEqual(len(rents), 0)

        # 搜索
        response = self.client.post(url_for('view_rents', q='te'))
        self.assertTrue(b'搜索结果' in response.data)

        # 所有出租信息
        response = self.client.post(url_for('view_rents'))
        self.assertTrue(b'所有出租信息' in response.data)

    def test_info(self):
        response = self.client.post(url_for('login'), data={
            'email': '123456789@qq.com',
            'password': '123'
        }, follow_redirects=True)

        # 我的收藏
        response = self.client.post(url_for('my_favourite'))
        self.assertTrue(b'我的收藏' in response.data)

        # 我的发布
        response = self.client.post(url_for('my_rent_publish'))
        self.assertTrue(b'我的发布' in response.data)