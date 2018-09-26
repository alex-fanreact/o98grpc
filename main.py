import time
from concurrent import futures
import util

import grpc

import pymongo
from bson.objectid import ObjectId

import other98_pb2 as other98_pb2
import other98_pb2_grpc as other98_pb2_grpc
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import MessageToDict


def get_post_view(collection: pymongo.collection, idstring: str) -> other98_pb2.PostView:
    raw=collection.find_one({'_id': ObjectId(idstring)})
    print(raw)
    postview = util.parse_post_view(raw)
    postview.id = idstring
    return postview


def get_post_feed(collection: pymongo.collection, postTags: [str], pageId='', pageSize:int=20):
    try:
        objectId = ObjectId(pageId)
        return collection.find({'$and': [{'postTags': {'$in': postTags}},
                                         {'_id': {'$gt': objectId}}]}).limit(pageSize)
    except:
        return collection.find({'postTags': {'$in': postTags}}).limit(pageSize)


def create_post(collection: pymongo.collection, post: other98_pb2.Post):
    postView = other98_pb2.PostView()
    postView.postSmallView.title = post.postSmallView.title
    postView.postSmallView.description = post.postSmallView.description
    postView.postSmallView.featuredImageLink = post.postSmallView.featuredImageLink
    postView.postSmallView.featuredVideoLink = post.postSmallView.featuredVideoLink
    postView.postSmallView.featuredCaption = post.postSmallView.featuredCaption
    postView.postSmallView.createDate = util.current_milli_time()
    postView.postSmallView.type = post.postSmallView.type
    postView.postSmallView.authorHandle = post.postSmallView.authorHandle
    postView.postTags.extend(post.postTags)
    postView.contentBlocks.extend(post.contentBlocks)
    postView.comments.extend([])
    collection.insert_one(util.parse_to_document(postView))


def update_post(postview_collection: pymongo, updated_postvew: other98_pb2.PostView):
    postview_collection.replace_one({'_id': ObjectId(updated_postvew.id)}, util.parse_to_document(updated_postvew))


def create_comment(collection: pymongo.collection, comment: other98_pb2.Comment):
    if comment.postViewId:
        postview = get_post_view(collection, comment.postViewId)
        i = 0
        for com in postview.comments:
            i += 1
        comment.id = i
        comment.score = 0
        comment.createDateMillis = util.current_milli_time()
        postview.comments.extend([comment])
        update_post(collection, postview)
    else:
        return


def get_comment(postview_collection: pymongo.collection, postview_id: str, comment_id: int) -> other98_pb2.Comment:
    postview = get_post_view(postview_collection, postview_id)
    if postview:
        for index, item in enumerate(postview.comments):
            if item.id == comment_id:
                return item


def update_comment(postview_collection: pymongo.collection, postview_id: str, comment_id: int, comment: other98_pb2.Comment):
    postview = get_post_view(postview_collection, postview_id)
    if postview:
        for index, item in enumerate(postview.comments):
            if item.id == comment_id:
                print(index)
                del postview.comments[index].contentBlocks[:]
                postview.comments[index].contentBlocks.extend(comment.contentBlocks)
                update_post(postview_collection, postview)
                break


def get_profile(collection: pymongo.collection, handle: str) -> other98_pb2.Profile:
    return util.parse_profile(collection.find_one({'handle': handle}))


class gRPCServer(other98_pb2_grpc.TheOther98Servicer):
    serverInstance = pymongo.MongoClient("mongodb://localhost:27017/")
    theOther98Db = serverInstance["theOther98Test"]
    profilesCollection = theOther98Db["profiles"]
    postsCollection = theOther98Db["posts"]

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