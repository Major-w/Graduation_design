# coding:utf-8
import unittest
import os
from flask import current_app,url_for
from flask_login import current_user
from web.app import app, db
from DB import orm
app.config['WTF_CSRF_ENABLED'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+pg8000://postgres:123123@localhost/graduation'


class GraduationBulletinTest(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(use_cookies=True)
        db.create_all()
        test_user = orm.User(email='123456789@qq.com', username='testuser', password='123', role_id=1, confirmed=True)
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
            bulletins= orm.Bulletin.query.filter_by(author_id=result.id).all()
            for bulletin in bulletins:
                orm.db.session.delete(bulletin)
            orm.db.session.commit()
        except:
            pass
        try:
            result = orm.User.query.filter_by(email='123456789@qq.com').one()
            orm.db.session.delete(result)
            orm.db.session.commit()
        except:
            pass

    def test_bulletin(self):

        response = self.client.post(url_for('login'), data={
            'email': '123456789@qq.com',
            'password': '123'
        }, follow_redirects=True)

        # 新建新闻公告
        response = self.client.post(url_for('view_bulletin'), data={
            'title': 'test',
            'content': 'test_content',
            'source': 'test_source'
        })
        user_id = orm.User.query.filter_by(email='123456789@qq.com').one().id
        bulletin = orm.Bulletin.query.filter_by(author_id=user_id).one()
        self.assertTrue(bulletin.title,'test')

        # 搜索
        response = self.client.post(url_for('view_bulletins', q='te'))
        self.assertTrue(b'搜索结果' in response.data)

        # 所有新闻公告
        response = self.client.post(url_for('view_bulletins'))
        self.assertTrue(b'所有公告' in response.data)

    def test_accounts(self):
        response = self.client.get(url_for('view_accounts'))
        self.assertTrue(b'所有用户' in response.data)
