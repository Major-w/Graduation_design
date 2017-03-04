'''
Created on 2013-8-5

@author: E525649
'''
import ctypes

asscii_string = lambda s: ''.join(map(lambda c: "%02X " % ord(c), s))

def int32_to_uint32(i):
    return ctypes.c_uint32(i).value

def hex8(n):
    return "0x%s"%("00000000%s"%(hex(n&0xffffffff)[2:-1]))[-8:]

import re
def validateEmail(email):
    if len(email) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
            return True
    return False

def validateMobilePhone(mobile_phone):
    if len(mobile_phone) > 7:
        #if re.match("^1(3[0-9]|5[0-35-9]|8[025-9])\\d{8}$", mobile_phone) != None:
        if re.match("^1\\d{10}$", mobile_phone) != None:
            return True
    return False

import socket, ssl, json, struct
import binascii
import urllib
import time, os, sys


def push_ios(tokens,message_type,content):
    for token in tokens:
	try:
            push_ios_release([token],message_type,content)
            pass
        except Exception, e:
            print e
            pass

        try:
            push_ios_test([token],message_type,content)
            pass
        except Exception, e:
            print e
            print(sys.exc_info()[0])
            pass

def push_ios_release(tokens,message_type,content):
    print "push (release): ",content," to ",tokens
    # device token returned when the iPhone application
    # registers to receive alerts
    #deviceToken = 'fcd2b568a140331e0125d4fba658fec8a11b26061c19e9eb7c7f4ad8a05014a6' 
    
    thePayLoad = {'aps':{'alert':content,'sound':'default','badge':0,},'sbs': { 'message_type': message_type },} 
    # Certificate issued by apple and converted to .pem format with openSSL
    # theCertfile = './Development_v3.pem'
    print "....."
    theCertfile = os.path.join(os.path.dirname(os.path.abspath(__file__)),'Development_v3.pem')
    print "=-----",theCertfile
    # 
    theHost = ( 'gateway.push.apple.com', 2195 ) 
    #theHost=('gateway.sandbox.push.apple.com',2195)
    # 
    data = json.dumps( thePayLoad ) 
    theNotification=""
    for token in tokens:
        deviceToken=token
        # Clear out spaces in the device token and convert to hex
        deviceToken = deviceToken.replace(' ','')
        # byteToken = bytes.fromhex( deviceToken )
        byteToken = binascii.unhexlify(deviceToken) 
        print("HELLOS_release")
        print(byteToken),"++", token
        theFormat = '!BH32sH%ds' % len(data)
        theNotification += struct.pack( theFormat, 0, 32, byteToken, len(data), data ) 

    # Create our connection using the certfile saved locally
    ssl_sock = ssl.wrap_socket( socket.socket( socket.AF_INET, socket.SOCK_STREAM ), certfile = theCertfile )
    ssl_sock.connect( theHost ) 
    # Write out our data
    ssl_sock.write( theNotification ) 
    
    #print ssl_sock.read()
    # Close the connection -- apple would prefer that we keep
    # a connection open and push data as needed.
    ssl_sock.close()
    print "push finished" 

def push_ios_test(tokens,message_type,content):
    print "push (test): ",content," to ",tokens
    # device token returned when the iPhone application
    # registers to receive alerts
    #deviceToken = 'fcd2b568a140331e0125d4fba658fec8a11b26061c19e9eb7c7f4ad8a05014a6' 
    
    thePayLoad = {'aps':{'alert':content,'sound':'default','badge':0,},'sbs': { 'message_type': message_type },} 
    # Certificate issued by apple and converted to .pem format with openSSL
    theCertfile =  os.path.join(os.path.dirname(os.path.abspath(__file__)),'Development_test.pem')
    print theCertfile
    # 
    #theHost = ( 'gateway.push.apple.com', 2195 ) 
    theHost=('gateway.sandbox.push.apple.com',2195)
    # 
    data = json.dumps( thePayLoad ) 
    theNotification=""
    for token in tokens:
        deviceToken=token
        # Clear out spaces in the device token and convert to hex
        deviceToken = deviceToken.replace(' ','')
        # byteToken = bytes.fromhex( deviceToken )
        byteToken = binascii.unhexlify(deviceToken) 
        print("HELLOS_test")
        print(byteToken),"++", token
        theFormat = '!BH32sH%ds' % len(data)
        theNotification += struct.pack( theFormat, 0, 32, byteToken, len(data), data ) 

    # Create our connection using the certfile saved locally
    ssl_sock = ssl.wrap_socket( socket.socket( socket.AF_INET, socket.SOCK_STREAM ), certfile = theCertfile )
    ssl_sock.connect( theHost ) 
    # Write out our data
    ssl_sock.write( theNotification ) 
    
    #print ssl_sock.read()
    # Close the connection -- apple would prefer that we keep
    # a connection open and push data as needed.
    ssl_sock.close()
    print "push finished" 


def GenAlarmMessage(session,sms_template, apartment, alarm_type, device_name):
    ISOTIMEFORMAT='%Y-%m-%d %X'
    strTime = time.strftime(ISOTIMEFORMAT, time.localtime())
    if apartment not in session:
        from DB import SBDB_ORM
        apartment = session.query(SBDB_ORM.Apartment).get(apartment.id)
    sms_template=sms_template.replace("[apartment]", apartment.account.user_name)
    sms_template=sms_template.replace("[time]",strTime)
    sms_template=sms_template.replace("[type]",alarm_type)
    sms_template=sms_template.replace("[device]",device_name)
    #sms_template= urllib.quote(sms_template.encode('gbk'))

    return sms_template
    
    
import uuid
def GenUUID():
    id_raw=str(uuid.uuid4())
    return id_raw.replace("-","")


import datetime
def GenRestoreURL(account_id):
    from DB import SBDB, SBDB_ORM
    uuid_restore=GenUUID()
    with SBDB.session_scope() as session :
        restore=SBDB_ORM.RestoreRequire()
        restore.account_id=account_id
        restore.dt=datetime.datetime.now()
        restore.finished=False
        restore.uuid=uuid_restore
        session.add(restore)
        session.commit()
    return "https://www.honhome.com/customer/reset_password/"+uuid_restore



def hash_password(password):
    from werkzeug.security import generate_password_hash
    return generate_password_hash(password)

def check_password(password,hashed_password):
    from werkzeug.security import check_password_hash
    return check_password_hash(hashed_password, password)

def GetMachineIPs():
    return socket.gethostbyname_ex(socket.gethostname())[2]


import platform
platform_system=platform.system().lower()
def isWindows():
    return platform_system.find("win")>=0


import os.path  

def file_extension(path):  
    return os.path.splitext(path)[1]  


import requests, urllib
def SendSMSByZA(mobile_phone, content):
    q_value = '&mobile=%s&content=%s&sendTime=&extno='% (urllib.quote(mobile_phone.encode('utf-8')), urllib.quote(content.encode('utf-8')))
    url_send = "http://www.591duanxin.com/sms.aspx?action=send&userid=539&account=rongshi106&password=123456%s"%q_value
    print url_send
    print requests.get(url_send).text
