#-*- coding: utf-8 -*-
from web.app import app, api
import json, threading, datetime
from DB import orm
from Logic import logic, restful
import os
from flask import Flask, request
from flask_restful import Resource, Api
import flask.ext.restless
from flask.ext.restless import ProcessingException

from web import views



def post_get_one(result=None, **kw):
    if result:
        logic.SetDefaultImage(result)
    return result

def post_get_many(result=None, search_params=None, **kw):
    if result and result.has_key(restful.ITEM_OBJECTS):
        for obj in result[restful.ITEM_OBJECTS]:
            logic.SetDefaultImage(obj)
    return result

def backup_pre_put_single_account(instance_id=None, data=None, **kw):
    if instance_id is None: return 
    account = orm.Account.query.filter_by(username=instance_id).first()
    if account is None:
        account = orm.Account(instance_id, None, None, None,0,0,None)
        orm.db.session.add(account)
        orm.db.session.commit()
    if data.has_key(restful.ITEM_CODE):
        terminal = orm.Terminal.query.filter_by(code=data[restful.ITEM_CODE]).first()
        if terminal is None:
            terminal = orm.Terminal(account.id,data.get(restful.ITEM_OS), data[restful.ITEM_CODE])
            orm.db.session.add(terminal)
        terminal.account_id = account.id
        terminal.os = data.get(restful.ITEM_OS)
        orm.db.session.commit()
    data.pop(restful.ITEM_CODE,None)
    data.pop(restful.ITEM_OS,None)

def pre_put_single_account(instance_id=None, data=None, **kw):
    if instance_id is None: return 
    # account = orm.Account.query.get(int(instance_id))
    # if account is None:
    #     return
    if data.has_key(restful.ITEM_CHECKCODE):
        dtNow = datetime.datetime.now()
        dtValidTime = account.dtcreate if account.dtcreate else datetime.datetime.now()
        dtValidTime = dtValidTime + datetime.timedelta(minutes=15)
        if account.checkcode == data.get(restful.ITEM_CHECKCODE) and dtNow < dtValidTime:
            account.flag_telephone = 1
            orm.db.session.commit()
    if data.has_key(restful.ITEM_TELEPHONE):
        if account.telephone!=data.get(restful.ITEM_TELEPHONE):
            account.flag_telephone = 0
            orm.db.session.commit()
    data.pop(restful.ITEM_FLAG_TELEPHONE,None)
    data.pop(restful.ITEM_CHECKCODE,None)


def pre_post_account(data=None, **kw):
    """Accepts a single argument, `data`, which is the dictionary of
    fields to set on the new instance of the model.

    """    
    if not data.has_key(restful.ITEM_USERNAME):
        data[restful.ITEM_USERNAME] = data.get(restful.ITEM_TELEPHONE)
    data[restful.ITEM_DTCREATE]=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pass


# import random
# def post_post_account(result=None, **kw):
#     """Accepts a single argument, `result`, which is the dictionary
#     representation of the created instance of the model.
#
#     """
#     if result and result.has_key(restful.ITEM_ID):
#         account = orm.Account.query.get(int(result.get(restful.ITEM_ID)))
#         account.checkcode = str(random.randint(100001,999999))
#         orm.db.session.commit()
#         #send sms verification here
#         message = '您的验证码为%s, 请勿告诉他人，15分钟有效 【学莫愁】' % account.checkcode
#         Util.SendSMSByZA(account.telephone, message)
#     return result
#     pass


def pre_post_test(data=None, **kw):
    if not data.has_key(restful.ITEM_USERNAME):
        data[restful.ITEM_USERNAME] = data.get(restful.ITEM_TELEPHONE)
    pass


# Create the Flask-Restless API manager.
orm.db.create_all()
manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=orm.db)

# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.
manager.create_api(orm.Area, methods=['GET'], url_prefix='/bd/api/v1.0')
manager.create_api(orm.Bulletin, methods=['GET'], url_prefix='/bd/api/v1.0', postprocessors={'GET_SINGLE': [post_get_one],'GET_MANY':[post_get_many]})
manager.create_api(orm.Rent, methods=['GET'], url_prefix='/bd/api/v1.0', postprocessors={'GET_SINGLE': [post_get_one],'GET_MANY':[post_get_many]})


class Messages(Resource):
    def post(self):
        pass
        print "POST a Message:", request.data,"--"
        body = json.loads(request.data)
        if body[ProtocolItem.MESSAGES][ProtocolItem.DEST_TYPE] == ProtocolItem.VALUE_IOS:
            threading.Thread(target=Util.push_ios,args=([body[ProtocolItem.MESSAGES][ProtocolItem.DEST_ID]], "alarm", body[ProtocolItem.MESSAGES][ProtocolItem.CONTENT])).start()
#            Util.push_ios([body[ProtocolItem.MESSAGES][ProtocolItem.DEST_ID]], 'alarm', body[ProtocolItem.MESSAGES][ProtocolItem.CONTENT])
        return {'_id':'0'}

    def get(self):
        return {'get':'None'}


api.add_resource(Messages, '/bd/api/messages')



if __name__ == '__main__':
    app.run(debug=True,port= 5001)












