from pymongo import MongoClient
import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),os.path.pardir))
from Utils import ProtocolItem

mongo_uri = 'mongodb://localhost:27017/'


def UpsertGateway(gateway):
    client = MongoClient(mongo_uri).hsg_cloud
    if gateway.has_key(ProtocolItem.ID) and gateway.has_key(ProtocolItem.VERSION):
        result = client.gateway.replace_one({ProtocolItem.ID:gateway[ProtocolItem.ID]},gateway,upsert=True)
        if result.upserted_id is None and result.modified_count>0:
            return client.gateway.find_one({ProtocolItem.ID:gateway[ProtocolItem.ID]})['_id']
        else:
            return result.upserted_id
    return None


def DeleteGateway(gateway):
    client = MongoClient(mongo_uri).hsg_cloud
    if gateway.has_key(ProtocolItem.ID):
        return client.gateway.delete_many({ProtocolItem.ID:gateway[ProtocolItem.ID]}).deleted_count
    else:
        return None


def GetGatewayVersion(gateway):
    client = MongoClient(mongo_uri).hsg_cloud
    if gateway.has_key(ProtocolItem.ID):
        return client.gateway.find_one({ProtocolItem.ID:gateway[ProtocolItem.ID]})[ProtocolItem.VERSION]
    else:
        return None


def GetGateway(gateway_id):
    client = MongoClient(mongo_uri).hsg_cloud
    return client.gateway.find_one({ProtocolItem.ID:gateway[ProtocolItem.ID]})[ProtocolItem.VERSION]
    if gateway.has_key(ProtocolItem.ID):
        return client.gateway.find_one({ProtocolItem.ID:gateway[ProtocolItem.ID]})
    else:
        return None


