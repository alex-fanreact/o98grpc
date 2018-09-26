import time
from datetime import datetime, timezone, timedelta
from concurrent import futures
import util

import grpc

import pymongo
from bson.objectid import ObjectId

import other98_pb2 as other98_pb2
import other98_pb2_grpc as other98_pb2_grpc
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import MessageToDict


def get_post_view(collection: pymongo.collection, idstring: str = '', object_id: ObjectId = None) -> other98_pb2.PostView:
    if idstring and idstring != '' and idstring != "":
        raw = collection.find_one({'_id': ObjectId(idstring)})
        postview = util.parse_post_view(raw)
        postview.id = idstring
        return postview
    elif object_id:
        raw = collection.find_one({'_id': object_id})
        postview = util.parse_post_view(raw)
        postview.id = str(object_id)
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
    # postView.postSmallView.featuredVideoLink = post.postSmallView.featuredVideoLink
    # postView.postSmallView.featuredCaption = post.postSmallView.featuredCaption
    postView.postSmallView.createDate = util.current_milli_time()
    postView.postSmallView.type = post.postSmallView.type
    postView.postSmallView.authorHandle = post.postSmallView.authorHandle
    postView.postTags.extend(post.postTags)
    postView.contentBlocks.extend(post.contentBlocks)
    postView.comments.extend([])
    collection.insert_one(util.parse_to_document(postView))


def update_post(postview_collection: pymongo, updated_postview: other98_pb2.PostView, allow_update_comments=False):
    currentpostview = get_post_view(postview_collection, updated_postview.id)
    if updated_postview.postSmallView:
        if updated_postview.postSmallView.title and updated_postview.postSmallView.title != '':
            currentpostview.postSmallView.title = updated_postview.postSmallView.title
        currentpostview.postSmallView.description = updated_postview.postSmallView.description
        currentpostview.postSmallView.featuredImageLink = updated_postview.postSmallView.featuredImageLink
        currentpostview.postSmallView.type = updated_postview.postSmallView.type
    # content blocks
    if updated_postview.contentBlocks:
        del currentpostview.contentBlocks[:]
        currentpostview.contentBlocks.extend(updated_postview.contentBlocks)
    # comments if necessary
    if updated_postview.comments and len(updated_postview.comments) > 0 and allow_update_comments:
        del currentpostview.comments[:]
        currentpostview.comments.extend(updated_postview.comments)
    postview_collection.replace_one({'_id': ObjectId(updated_postview.id)}, util.parse_to_document(currentpostview))


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
        update_post(collection, postview, True)
    else:
        return


def get_comment(postview_collection: pymongo.collection, postview: other98_pb2.PostView, comment_id: int) -> other98_pb2.Comment:
    if postview:
        for index, item in enumerate(postview.comments):
            if item.id == comment_id:
                return item


def update_comment(postview_collection: pymongo.collection, postview: other98_pb2.PostView, comment_id: int, comment: other98_pb2.Comment):
    if postview:
        for index, item in enumerate(postview.comments):
            if item.id == comment_id:
                print(index)
                # delete old content blocks and attach new edited ones
                postview.comments[index].text = comment.text
                # update post and break
                update_post(postview_collection, postview, True)
                break


def get_profile(collection: pymongo.collection, handle: str) -> other98_pb2.Profile:
    return util.parse_profile(collection.find_one({'handle': handle}))


def update_profile(collection: pymongo.collection, handle: str, profile: other98_pb2.Profile):
    current_profile = get_profile(collection, handle)


LOG_GET_REQUEST = "\n**GET REQUEST**\n"


def get_utc_time():
    return datetime.now(timezone.utc)


def log_get_request(description: str, request, context):
    log = str(get_utc_time()) + LOG_GET_REQUEST + description + '\nCONTEXT: ' + str(context) + '\nREQUEST \n' + str(request)
    print(log)
    return log


def log_result(result, request_log: str):
    print(str(get_utc_time()) + '\n**RETURN**\n' + str(result) + request_log)


class gRPCServer(other98_pb2_grpc.TheOther98Servicer):
    serverInstance = pymongo.MongoClient("mongodb://localhost:27017/")
    theOther98Db = serverInstance["theOther98Test"]
    profilesCollection = theOther98Db["profiles"]
    postsCollection = theOther98Db["posts"]

    def __init__(self):
        print('init')

    def GetPost(self, request, context):
        request_log = log_get_request('get post request', request, context)
        postview = get_post_view(gRPCServer.postsCollection, request.value)
        log_result(postview, request_log)
        return postview
    
    def GetFeed(self, request, context):
        request_log = log_get_request('get post feed', request, context)
        posttags = ['']
        for tag in request.postTags:
            posttags.append(tag)
        pageId = request.pageId
        pageSize = request.pageSize
        cursor = get_post_feed(gRPCServer.postsCollection, postTags=posttags, pageId=pageId, pageSize=pageSize)
        try:
            obj = cursor.next()
            while obj:
                try:
                    log_result(util.parse_post_view(obj), request_log)
                    yield util.parse_post_view(obj)
                    obj = cursor.next()
                except StopIteration:
                    return
        except StopIteration:
            return

    def GetProfile(self, request, context):
        request_log = log_get_request('get profile', request, context)
        profile = get_profile(gRPCServer.profilesCollection, request.value)
        log_result(profile, request_log)
        return profile

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