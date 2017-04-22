# coding:utf-8
import unittest
import os
from flask import current_app,url_for
from flask_login import current_user
from web.app import app, db
from DB import orm
app.config['WTF_CSRF_ENABLED'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+pg8000://postgres:rootroot@localhost/Graduation'


class GraduationDemandTest(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(use_cookies=True)
        db.create_all()
        test_user = orm.User(email='123456789@qq.com', username='testuser', password='123', role_id=2, confirmed=True)
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
            demands= orm.Demand.query.filter_by(author_id=result.id).all()
            for demand in demands:
                orm.db.session.delete(demand)
            orm.db.session.commit()
        except:
            pass
        try:
            result = orm.User.query.filter_by(email='123456789@qq.com').one()
            orm.db.session.delete(result)
            orm.db.session.commit()
        except:
            pass

    def test_demand(self):

        response = self.client.post(url_for('login'), data={
            'email': '123456789@qq.com',
            'password': '123'
        }, follow_redirects=True)

        # 新建求租信息
        response = self.client.post(url_for('view_demand'), data={
            'contacts': 'test',
            'phone_number': 123456,
            'area_id': 2,
            'mode_id': 1,
            'decorate_type': '0',
            'subway_line': 2,
            'price_low': 1000,
            'price_high': 2000,
            'description': 'xxxxxx',
            'title': 'test'
        })
        user_id = orm.User.query.filter_by(email='123456789@qq.com').one().id
        demand = orm.Demand.query.filter_by(author_id=user_id).one()
        self.assertTrue(demand.title,'test')

        # 收藏
        response = self.client.post(url_for('view_rent_int', like_rent_id=33))
        like = orm.Like.query.filter_by(user_id=user_id,rent_id=33).all()
        self.assertEqual(len(like),1)

        # 取消收藏
        response = self.client.post(url_for('view_rent_int', unlike_rent_id=33))
        like = orm.Like.query.filter_by(user_id=user_id, rent_id=33).all()
        self.assertEqual(len(like),0)

        # 我的发布
        response = self.client.post(url_for('my_demand_publish'))
        self.assertTrue(b'我的发布' in response.data)

        # 我的发布(删除)
        response = self.client.get(url_for('my_demand_publish', delete_demand_id=demand.id))
        demands = orm.Demand.query.filter_by(author_id=user_id,id=demand.id).all()
        self.assertEqual(len(demands), 0)

        # 搜索
        response = self.client.post(url_for('view_demands',q='te'))
        self.assertTrue(b'搜索结果' in response.data)

        # 所有求租信息
        response = self.client.post(url_for('view_demands'))
        self.assertTrue(b'所有求租信息' in response.data)
