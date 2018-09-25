import time
from concurrent import futures

import grpc

import pymongo
from bson.objectid import ObjectId

import other98_pb2 as other98_pb2
import other98_pb2_grpc as other98_pb2_grpc


def getPostFromDb(collection, idstring):
    return collection.find_one({'_id': ObjectId(idstring)})

def getPostFeed(collection, *postTags, pageId='', pageSize=20):
    try:
        objectId = ObjectId(pageId)
        return collection.find({'$and': [{'postTags': {'$in': postTags}},
                                         {'_id': {'$gt': objectId}}]}).limit(pageSize)
    except:
        return collection.find({'postTags': {'$in': postTags}}).limit(pageSize)


class gRPCServer(other98_pb2_grpc.TheOther98Servicer):
    serverInstance = pymongo.MongoClient("mongodb://localhost:27017/")
    theOther98Db = serverInstance["theOther98Test"]

    postTags = ['forum']
    feed = getPostFeed(theOther98Db.posts, *postTags, pageId='5ba84cb730341313fc6a42df', pageSize=20)
    obj = next(feed, None)
    if obj:
        print(obj)

    def __init__(self):
        print('init')
    
    def GetFeed(self, request, context):
        # postFeedView = other98_pb2.PostFeedView()
        # postFeedView.posts = gRPCServer.theOther98Db["posts"].find()
        for x in gRPCServer.serverInstance["theOther98Test"]["posts"].find(request.pageSize):
            print(x)
        return other98_pb2.PostFeedView(id = 'id')

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    other98_pb2_grpc.add_TheOther98Servicer_to_server(
        gRPCServer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            continue
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()