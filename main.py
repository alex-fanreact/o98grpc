import time
from datetime import datetime, timezone, timedelta
from concurrent import futures
import util

import grpc

import pymongo
import copy
from bson.objectid import ObjectId

import other98_pb2 as other98_pb2
import other98_pb2_grpc as other98_pb2_grpc
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import MessageToDict

default_roles_viewable = ['user', 'anonymous']

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


def create_post(collection: pymongo.collection, post: other98_pb2.Post, roles_viewable: [str]):
    if post.postSmallView.title is None or post.postSmallView.title == '':
        # TODO: inform user
        return
    postView = other98_pb2.PostView()
    postView.postSmallView.CopyFrom(post.postSmallView)
    postView.postSmallView.createDate = util.current_milli_time()
    # TODO: assign authorHandle by signed in user
    postView.postTags.extend(post.postTags)
    postView.contentBlocks.extend(post.contentBlocks)
    postView.comments.extend([])
    dictionary = util.parse_to_document(postView)
    dictionary["roles"] = roles_viewable
    return collection.insert_one(dictionary).inserted_id


def update_post(postview_collection: pymongo, updated_postview: other98_pb2.PostView, allow_update_comments=False, updated_roles_viewable: [str] = None):
    try:
        raw_post = postview_collection.find_one({'_id': updated_postview.id})
    except:
        raw_post = None
    currentpostview = get_post_view(postview_collection, updated_postview.id)
    if currentpostview is None:
        return
    if updated_postview.postSmallView:
        if updated_postview.postSmallView.title is None or updated_postview.postSmallView.title == '':
            updated_postview.postSmallView.title = currentpostview.postSmallView.title
        currentpostview.postSmallView.CopyFrom(updated_postview.postSmallView)
    # content blocks
    if updated_postview.contentBlocks:
        del currentpostview.contentBlocks[:]
        currentpostview.contentBlocks.extend(updated_postview.contentBlocks)
    # comments if necessary
    if updated_postview.comments and len(updated_postview.comments) > 0 and allow_update_comments:
        del currentpostview.comments[:]
        currentpostview.comments.extend(updated_postview.comments)
    dictionary = util.parse_to_document(currentpostview)
    if updated_roles_viewable:
        dictionary["roles"] = updated_roles_viewable
    else:
        if raw_post:
            try:
                dictionary["roles"] = raw_post["roles"]
            except:
                dictionary["roles"] = default_roles_viewable
        else:
            dictionary["roles"] = default_roles_viewable
    postview_collection.replace_one({'_id': ObjectId(updated_postview.id)}, dictionary)


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
LOG_POST_REQUEST = "\n**POST REQUEST**\n"


def get_utc_time():
    return datetime.now(timezone.utc)


def log_get_request(description: str, request, context):
    log = str(get_utc_time()) + LOG_GET_REQUEST + description + '\nCONTEXT: ' + str(context) + '\nREQUEST \n' + str(request)
    print(log)
    return log


def log_post_request(description: str, request, context):
    log = str(get_utc_time()) + LOG_POST_REQUEST + description + '\nCONTEXT: ' + str(context) + '\nREQUEST \n' + str(request)
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
        # collect request information
        for tag in request.postTags:
            posttags.append(tag)
        pageId = request.pageId
        pageSize = request.pageSize
        # prepare objects for response
        feed_response_view = other98_pb2.FeedResponseView()
        post_feed_views = []
        cursor = get_post_feed(gRPCServer.postsCollection, postTags=posttags, pageId=pageId, pageSize=pageSize)
        try:
            obj = cursor.next()
            while obj:
                try:
                    postview = util.parse_post_view(obj)
                    pfv = other98_pb2.PostFeedView()
                    pfv.postViewId = str(obj['_id'])
                    # pfv.postSmallView.__dict__.update(postview.postSmallView.__dict__)
                    pfv.postSmallView.CopyFrom(postview.postSmallView)
                    pfv.numberOfComments = len(postview.comments)
                    pfv.dateOfLastComment = postview.comments[pfv.numberOfComments - 1].createDateMillis
                    post_feed_views.append(pfv)
                    obj = cursor.next()
                except StopIteration:
                    break
        except StopIteration:
            obj = None
        for post in post_feed_views:
            feed_response_view.postFeedViews.extend([post])
            feed_response_view.nextPageId = post.postViewId
        log_result(result=feed_response_view, request_log=request_log)
        return feed_response_view

    def GetProfile(self, request, context):
        request_log = log_get_request('get profile', request, context)
        profile = get_profile(gRPCServer.profilesCollection, request.value)
        log_result(profile, request_log)
        return profile

    def CreatePost(self, request, context):
        request_log = log_post_request('create post', context, request)
        viewable_roles = []
        for role in request.viewable_roles:
            viewable_roles.append(role)
        if len(viewable_roles) == 0:
            viewable_roles = default_roles_viewable
        post = request.post
        result_id = create_post(gRPCServer.postsCollection, post, viewable_roles)
        result = other98_pb2.Result()
        if result_id:
            result.statusCode = 0
            log_result(result, request_log)
            yield result
        else:
            result.statusCode = 4
            result.errorMessage = 'Post was not entered into database'
            log_result(result, request_log)
            yield result

    def CreateComment(self, request, context):
        request_log = log_post_request('create comment', context, request)
        result = other98_pb2.Result()
        comment = request
        if comment.postViewId is None or comment.postViewId == '':
            result.statusCode = 3
            result.errorMessage = 'Please attach a postview ID'
            return result
        # TODO: assign comment.authorHandle
        comment.score = 0
        comment.createDateMillis = util.current_milli_time()
        postview = get_post_view(gRPCServer.postsCollection, comment.postViewId)
        create_comment(gRPCServer.postsCollection, comment)
        postview1 = get_post_view(gRPCServer.postsCollection, comment.postViewId)
        if len(postview1.comments) > len(postview.comments):
            result.statusCode = 0
            log_result(result, request_log)
            return result
        else:
            result.statusCode = 4
            result.errorMessage = 'An error occurred while inserting the comment'
            log_result(result, request_log)
            return result


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    other98_pb2_grpc.add_TheOther98Servicer_to_server(
        gRPCServer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(1)
            continue
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()