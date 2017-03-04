from Utils import Util
import requests, json



gateway = {
    'id':'xxxxxxxyy1',
    'Name':'...test gateway.1.',
    'version':23,
    'Devices':[
     {
         'Id':11,
         'Dev_type': 'light',
         'Name': '.....',
         'Dev_model':'2012D',
         'Dev_code': '90010A58',
         'device_key':[
             {
                 'dev_key_seq':0,
                 'name': '...'
             },
             {
                 'dev_key_seq':2,
                 'name': '..22.'
             }
         ]
     }
    ],
    'Scenes':[
     {
         'Id':14,
         'Name': '..',
         'Scence_contents':[
             {
                 'Id':12,
                 'Dev_id': 9,
                 'dev_key_seq':1,
                 'value': 1  
             },
             {
                 'Id':13,
                 'Dev_id': 9,
                 'dev_key_seq':2,
                 'value': 2  
             }
         ]
     }   
    ],
    'Contactors':[
     {
         'Id':12,
         'Name':'...',
         'Mobile_phone': '139123xxxx'
     }    
    ],
    'Containers':[
     {
        'name':' ..',
        'device_ids':[2,34,11]
     }
    ]
}


def main():
#    print requests.get('http://121.42.12.11:81/a').text
#    return 
    root_url = "http://121.42.12.11:81/api"

    # test message push
    data = json.dumps({'messages':{'dest_type':'ios','dest_id':'fcd2b568a140331e0125d4fba658fec8a11b26061c19e9eb7c7f4ad8a05014a6','content':'test message'}, 'data':'some test repo'}) 
    print data
    print json.loads(data)
#    r = requests.post(root_url+'/messages', data, verify=False)
#    print 'result of push-message:', r.text
    
    # test Add Gateway
    request = {
        'version': 'xx',
        'addgateway':{
            'sessionid':'xxxxxxxxxxxxxxxxxxx',
            'gateway':gateway
        }
    }
    r = requests.post(root_url+'/gateway', json.dumps(request), verify=False)
    print 'result of add gateway:', r.text


    # test Update Gateway
    request = {
        'version': 'xx',
        'updategateway':{
            'sessionid':'xxxxxxxxxxxxxxxxxxx',
            'gateway':{    'id':'xxxxxxxyy1','property_test':1, 'version':23}
        }
    }
    r = requests.put(root_url+'/gateway/1', data=json.dumps(request), verify=False)
    print 'result of modify gateway:', r.text

    return
    
    # test Delete Gateway
    request = {
        'version': 'xx',
        'deletegateway':{
            'sessionid':'xxxxxxxxxxxxxxxxxxx',
            'gateway':{    'id':'xxxxxxxyy1','property_test':1}
        }
    }
    r = requests.delete(root_url+'/gateway/1', data=json.dumps(request), verify=False)
    print 'result of delete gateway', r.text

if __name__ == '__main__':
    main()
    
    pass
