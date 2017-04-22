#-*- coding: utf-8 -*-

ROOT_DOMAIN = 'http://192.168.0.73:5001'
ROOT_RESTFUL = ROOT_DOMAIN + '/bd/api/v1.0'

RESTFUL_RENT = ROOT_RESTFUL+'/rent'
RESTFUL_INSTITUTION = ROOT_RESTFUL+ '/institution'
RESTFUL_BULLETIN = ROOT_RESTFUL+ '/bulletin'
RESTFUL_ACCOUNT = ROOT_RESTFUL+ '/account'
RESTFUL_ACCOUNTBACK = ROOT_RESTFUL+ '/back/account'


ITEM_TOTAL_PAGES ='total_pages'
ITEM_PAGE = 'page'
ITEM_OBJECTS = 'objects'
ITEM_NUM_RESULTS = 'num_results'

ITEM_BULLETINIMAGES = 'bulletinimages'
ITEM_INSTITUTIONIMAGES = 'institutionimages'
ITEM_SCHOOLIMAGES = 'schoolimages'
ITEM_FILE = 'file'

ITEM_ID = 'id'
ITEM_NAME = 'name'

ITEM_CODE = 'code'
ITEM_OS = 'os'
ITEM_CHECKCODE = 'checkcode'
ITEM_FLAG_TELEPHONE = 'flag_telephone'
ITEM_TELEPHONE = 'telephone'
ITEM_USERNAME = 'username'
ITEM_SOURCE = 'source'
ITEM_DTCREATE = 'dtcreate'

import json, requests, urllib

def PostAccount(body):
    headers = {'Content-type': 'application/json'}
    data = json.dumps(body)
    return json.loads(requests.post('%s'%(RESTFUL_ACCOUNTBACK), data=data, headers=headers).text)

def GetRents(page, name=None):
    if name is None:
        x = requests.get('%s?page=%d'%(RESTFUL_RENT, page)).text
        return json.loads(x)
    else:
        q_value = '{"filters":[{"name":"name","op":"like","val":"%%%s%%"}]}'%name
        q_value=urllib.quote(q_value.encode('utf-8'))
        return json.loads(requests.get('%s?page=%d&q=%s'%(RESTFUL_RENT, page, q_value)).text)


def GetInstitutions(page, name=None):
    if name is None:
        return json.loads(requests.get('%s?page=%d'%(RESTFUL_INSTITUTION, page)).text)
    else:
        q_value = '{"filters":[{"name":"name","op":"like","val":"%%%s%%"}]}'%name
        q_value=urllib.quote(q_value.encode('utf-8'))
        return json.loads(requests.get('%s?page=%d&q=%s'%(RESTFUL_INSTITUTION, page, q_value)).text)


def GetBulletins(page, title=None):
    if title is None:
        return json.loads(requests.get('%s?page=%d'%(RESTFUL_BULLETIN, page)).text)
    else:
        q_value = '{"filters":[{"name":"title","op":"like","val":"%%%s%%"}]}'%title
        q_value=urllib.quote(q_value.encode('utf-8'))
        return json.loads(requests.get('%s?page=%d&q=%s'%(RESTFUL_BULLETIN, page, q_value)).text)


def GetPagingFromResult(result):
    total_pages=int(result[ITEM_TOTAL_PAGES])
    page = int(result[ITEM_PAGE])
    page_from = max(1,page-5)
    page_to = min(total_pages,page+5)
    return {'total_pages': total_pages, 'page': page, 'page_from':page_from, 'page_to': page_to}


def GetAccounts(page, title=None):
    if title is None:
        return json.loads(requests.get('%s?page=%d'%(RESTFUL_ACCOUNT, page)).text)
    else:
        q_value = '{"filters":[{"or":[{"name":"username","op":"like","val":"%%%s%%"},{"name":"name","op":"like","val":"%%%s%%"},{"name":"telephone","op":"like","val":"%%%s%%"}]}]}'% (title, title, title)
        q_value=urllib.quote(q_value.encode('utf-8'))
        return json.loads(requests.get('%s?page=%d&q=%s'%(RESTFUL_BULLETIN, page, q_value)).text)


def GetUsers(page, title=None):
    if title is None:
        return json.loads(requests.get('%s?page=%d'%(RESTFUL_ACCOUNT, page)).text)
    else:
        q_value = '{"filters":[{"or":[{"name":"username","op":"like","val":"%%%s%%"},{"name":"name","op":"like","val":"%%%s%%"},{"name":"telephone","op":"like","val":"%%%s%%"}]}]}'% (title, title, title)
        q_value=urllib.quote(q_value.encode('utf-8'))
        return json.loads(requests.get('%s?page=%d&q=%s'%(RESTFUL_BULLETIN, page, q_value)).text)
