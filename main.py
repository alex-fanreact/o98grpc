import time
from datetime import datetime, timezone, timedelta
from concurrent import futures

import util
import chat

import random
import string
import pymongo
from bson.objectid import ObjectId

import grpc
import other98_pb2 as other98_pb2
import other98_pb2_grpc as other98_pb2_grpc
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import MessageToDict
import json

role_user = 'user'
role_anonymous = 'anonymous'
property_name_roles = 'roles'
default_roles_viewable = [role_user, role_anonymous]


def get_post_view(collection: pymongo.collection, idstring: str = '', object_id: ObjectId = None, userHandle: str='') -> other98_pb2.PostView:
    result = other98_pb2.Result()
    if idstring and idstring != '' and idstring != "":
        raw = collection.find_one({'_id': ObjectId(idstring)})
        if userHandle is None or userHandle == '':
            raw = collection.find_one({'$and': [{'_id': ObjectId(idstring)},
                                                {property_name_roles: {'$in': [role_anonymous]}}]})
            if raw is None:
                postview = other98_pb2.PostView()
                result.statusCode = 1
                result.errorMessage = 'You are not allowed to view that post'
                return postview
        postview = util.parse_post_view(raw)
        postview.id = idstring
        if postview.postSmallView:
            result.statusCode = 0
            postview.result.CopyFrom(result)
        else:
            result.statusCode = 3
            result.statusCode = 'Post view with id ' + idstring + ' not found'
            postview.result.CopyFrom(result)
        postview.score = len(postview.postVotes)
        for vote in postview.postVotes:
            if vote.userHandle == userHandle:
                postview.userVote += vote.voteValue
        return postview
    elif object_id:
        raw = collection.find_one({'_id': object_id})
        if userHandle is None or userHandle == '':
            raw = collection.find_one({'$and': [{'_id': object_id},
                                                {property_name_roles: {'$in': [role_anonymous]}}]})
            if raw is None:
                postview = other98_pb2.PostView()
                result.statusCode = 1
                result.errorMessage = 'You are not allowed to view that post'
                postview.result.CopyFrom(result)
                return postview
        postview = util.parse_post_view(raw)
        postview.id = str(object_id)
        postview.result = other98_pb2.Result()
        if postview.postSmallView:
            result.statusCode = 0
            postview.result.CopyFrom(result)
        else:
            result.statusCode = 3
            result.errorMessage = 'Post view with id ' + str(object_id) + ' not found'
            postview.result.CopyFrom(result)
        postview.score = len(postview.postVotes)
        for vote in postview.postVotes:
            if vote.userHandle == userHandle:
                postview.userVote += vote.voteValue
        return postview


def get_post_feed(collection: pymongo.collection, postTags: [str], pageId='', pageSize:int=20, userHandle: str=''):
    post_feed_views = []
    try:
        objectId = ObjectId(pageId)
        cursor = collection.find({'$and': [{'postTags': {'$in': postTags}},
                                           {'_id': {'$gt': objectId}}]}).sort([('createDate', pymongo.ASCENDING)]).limit(pageSize)
        if userHandle is None or userHandle == '':
            cursor = collection.find({'$and': [{'postTags': {'$in': postTags}},
                                               {property_name_roles: {'$in': [role_anonymous]}},
                                               {'_id': {'$gt': objectId}}]}).sort([('createDate', pymongo.ASCENDING)]).limit(pageSize)
    except:
        cursor = collection.find({'postTags': {'$in': postTags}}).sort([('createDate', pymongo.ASCENDING)]).limit(pageSize)
        if userHandle is None or userHandle == '':
            cursor = collection.find({'$and': [{'postTags': {'$in': postTags}},
                                               {property_name_roles: {'$in': [role_anonymous]}}]}).sort([('createDate', pymongo.ASCENDING)]).limit(pageSize)
    try:
        obj = cursor.next()
        while obj:
            try:
                postview = util.parse_post_view(obj)
                print(str(postview.postTags))
                pfv = other98_pb2.PostFeedView()
                pfv.postViewId = str(obj['_id'])
                pfv.postSmallView.CopyFrom(postview.postSmallView)
                pfv.numberOfComments = len(postview.comments)
                if pfv.numberOfComments > 0:
                    pfv.dateOfLastComment = postview.comments[pfv.numberOfComments - 1].createDateMillis
                else:
                    pfv.dateOfLastComment = -1
                pfv.score = len(postview.postVotes)
                for vote in postview.postVotes:
                    if vote.userHandle == userHandle:
                        pfv.userVote += vote.voteValue
                post_feed_views.append(pfv)
                obj = cursor.next()
            except StopIteration:
                break
    except StopIteration:
        obj = None
    return post_feed_views


def create_post(collection: pymongo.collection, post: other98_pb2.Post, roles_viewable: [str]):
    if post.postSmallView.title is None or post.postSmallView.title == '' or post.postSmallView.authorHandle == '':
        # TODO: inform user
        return None
    postView = other98_pb2.PostView()
    postView.postSmallView.CopyFrom(post.postSmallView)
    postView.postSmallView.createDate = util.current_milli_time()
    # TODO: assign authorHandle by signed in user
    postView.postTags.extend(post.postTags)
    postView.contentBlocks.extend(post.contentBlocks)
    postView.comments.extend([])
    dictionary = util.parse_to_document(postView)
    dictionary[property_name_roles] = roles_viewable
    return collection.insert_one(dictionary).inserted_id


def update_post(postview_collection: pymongo, updated_postview: other98_pb2.PostView, overwrite_comments=False, updated_roles_viewable: [str] = None):
    try:
        raw_post = postview_collection.find_one({'_id': ObjectId(updated_postview.id)})
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
    if updated_postview.comments and len(updated_postview.comments) > 0 and overwrite_comments:
        del currentpostview.comments[:]
        currentpostview.comments.extend(updated_postview.comments)
    if updated_postview.postVotes and len(updated_postview.postVotes) > 0:
        del currentpostview.postVotes[:]
        currentpostview.postVotes.extend(updated_postview.postVotes)
    dictionary = util.parse_to_document(currentpostview)
    if updated_roles_viewable:
        dictionary[property_name_roles] = updated_roles_viewable
    else:
        if raw_post:
            try:
                dictionary[property_name_roles] = raw_post[property_name_roles]
            except:
                dictionary[property_name_roles] = default_roles_viewable
        else:
            dictionary[property_name_roles] = default_roles_viewable
    postview_collection.replace_one({'_id': ObjectId(updated_postview.id)}, dictionary)


def create_comment(collection: pymongo.collection, comment: other98_pb2.Comment):
    if comment.postViewId and comment.postViewId != '':
        postview = get_post_view(collection, comment.postViewId)
        if postview:
            i = len(postview.comments)
            # always non zero
            comment.id = i + 1
            comment.score = 0
            comment.createDateMillis = util.current_milli_time()
            postview.comments.extend([comment])
            update_post(collection, postview, True)
    else:
        return


def get_comment(postview: other98_pb2.PostView, comment_id: int) -> other98_pb2.Comment:
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
                postview.comments[index].CopyFrom(comment)
                # update post and break
                update_post(postview_collection, postview, True)
                break


def create_profile(collection: pymongo.collection, profile: other98_pb2.Profile):
    if profile.handle and profile.handle != '':
        return collection.insert_one(util.parse_to_document(profile)).inserted_id
    else:
        return None


def get_profile(collection: pymongo.collection, handle: str) -> other98_pb2.Profile:
    return util.parse_profile(collection.find_one({'handle': handle}))


def update_profile(collection: pymongo.collection, handle: str, profile: other98_pb2.Profile):
    current_profile = get_profile(collection, handle)
    # TODO: implement the rest


def get_comment_votes(postview: other98_pb2.PostView, commentId: int, userhandle: str) -> (int, int):
    if commentId > 0:
        for comment in postview.comments:
            if comment.id == commentId:
                total_votes = 0
                user_vote = 0
                for vote in comment.commentVotes:
                    total_votes += vote.voteValue
                    if vote.userHandle == userhandle:
                        user_vote += vote.voteValue
                return total_votes, user_vote
    return 0, 0


def vote_on_post(collection: pymongo.collection, post_vote: other98_pb2.PostVote):
        postview = get_post_view(collection, idstring=post_vote.postViewId, userHandle=post_vote.userHandle)
        if postview:
            voteReplaced = False
            for i in range(len(postview.postVotes)):
                if postview.postVotes[i].userHandle == post_vote.userHandle:
                    postview.postVotes[i].CopyFrom(post_vote)
                    update_post(collection, postview)
                    voteReplaced = True
                    return True
            if voteReplaced == False:
                postview.postVotes.extend([post_vote])
                update_post(collection, postview)
                return True
        return False


def vote_on_comment(collection: pymongo.collection, comment_vote: other98_pb2.CommentVote):
    if comment_vote and comment_vote.postViewId != '' and comment_vote.userHandle != '' and comment_vote.commentId != 0:
        postview = get_post_view(collection, idstring=comment_vote.postViewId, userHandle=comment_vote.userHandle)
        if postview:
            voteReplaced = False
            for comment_index in range(len(postview.comments)):
                comment = postview.comments[comment_index]
                if comment.id == comment_vote.commentId:
                    for comment_vote_index in range(len(comment.commentVotes)):
                        if comment.commentVotes[comment_vote_index].userHandle == comment_vote.userHandle:
                            comment.commentVotes[comment_vote_index].CopyFrom(comment_vote)
                            update_comment(collection, postview, comment.id, comment)
                            voteReplaced = True
                            return True
                    if voteReplaced == False:
                        comment.commentVotes.extend([comment_vote])
                        update_comment(collection, postview, comment.id, comment)
                        return True
        return False
    return False


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


def random_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


class gRPCServer(other98_pb2_grpc.TheOther98Servicer):
    database_name = 'theOther98Test'
    profiles_collection_name = 'profiles'
    posts_collection_name = 'posts'
    conversations_collection_name = 'conversations'
    messages_collection_name = 'messages'
    notifications_collection_name = 'notifications'
    # vote_collection_name_posts = 'votes_posts'
    # vote_collection_name_comments = 'votes_comments'

    serverInstance = pymongo.MongoClient("mongodb://localhost:27017/?replicaSet=rs")
    theOther98Db = serverInstance[database_name]
    profilesCollection = theOther98Db[profiles_collection_name]
    postsCollection = theOther98Db[posts_collection_name]
    conversationsCollection = theOther98Db[conversations_collection_name]
    messagesCollection = theOther98Db[messages_collection_name]
    notificationsCollection = theOther98Db[notifications_collection_name]

    def __init__(self):
        # create indexes
        gRPCServer.profilesCollection.create_index([('handle', pymongo.TEXT)], name='handle_index', unique=True)
        # gRPCServer.postsCollection.create_index(['postTags'])
        print('init')

    def GetPost(self, request, context):
        request_log = log_get_request('get post request', request, context)
        postview = get_post_view(gRPCServer.postsCollection, idstring=request.value, userHandle=request.authToken)
        log_result(postview, request_log)
        if postview:
            return postview
        else:
            return
    
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

        print("pageSize={pageSize}")
        if pageSize == 0: 
            pageSize = 20
            print("setting page size to 20")

        post_feed_views = get_post_feed(gRPCServer.postsCollection, postTags=posttags, pageId=pageId, pageSize=pageSize, userHandle=request.authToken)
        for post in post_feed_views:
            feed_response_view.postFeedViews.extend([post])
            feed_response_view.nextPageId = post.postViewId
        log_result(result=len(feed_response_view.postFeedViews), request_log=request_log)
        return feed_response_view

    def GetProfile(self, request, context):
        request_log = log_get_request('get profile', request, context)
        profile = get_profile(gRPCServer.profilesCollection, request.value)
        log_result(profile, request_log)
        profileresponseview = other98_pb2.ProfileResponseView()
        profileresponseview.profile.CopyFrom(profile)
        result = other98_pb2.Result()
        if profile:
            result.statusCode = 0
            profileresponseview.result.CopyFrom(result)
            return profileresponseview
        else:
            result.statusCode = 3
            result.errorMessage = 'Post with ID: ' + request.value + ' not found'
            profileresponseview.result.CopyFrom(result)
            return profileresponseview

    def CreatePost(self, request, context):
        request_log = log_post_request('create post', request, context)
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
            result.createdId = str(result_id)
            log_result(result, request_log)
            return result
        else:
            result.statusCode = 4
            result.errorMessage = 'Post was not entered into database'
            log_result(result, request_log)
            return result

    def CreateComment(self, request, context):
        request_log = log_post_request('create comment', request, context)
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

    def VoteOnPost(self, request, context):
        request_log = log_post_request('vote on post', request, context)
        result = other98_pb2.Result()
        if request.postViewId == '' or request.userHandle == '':
            result.statusCode = 3
            result.errorMessage = 'Please attach postViewId and userHandle to request'
            log_result(result, request_log)
            return result
        else:
            operation_success = vote_on_post(gRPCServer.postsCollection, request)
            if operation_success:
                result.statusCode = 0
                log_result(result, request_log)
                return result
            else:
                result.statusCode = 4
                result.errorMessage = 'The write operation was unsuccessful, please try again'
                log_result(result, request_log)
                return result

    def VoteOnComment(self, request, context):
        request_log = log_post_request('vote on comment', request, context)
        result = other98_pb2.Result()
        if request.postViewId == '' or request.userHandle == '' or request.commentId == 0:
            result.statusCode = 3
            result.errorMessage = 'Please attach postViewId, userHandle and commentId to request'
            log_result(result, request_log)
            return result
        else:
            operation_success = vote_on_comment(gRPCServer.postsCollection, request)
            if operation_success:
                result.statusCode = 0
                log_result(result, request_log)
                return result
            else:
                result.statusCode = 4
                result.errorMessage = 'The write operation was unsuccessful, please try again'
                log_result(result, request_log)
                return result

    def GetMyConversations(self, request, context):
        request_log = log_get_request('get my conversations', request, context)
        authToken = request.authToken
        # get username here when possible, for now auth token will be the username
        cursor = chat.get_current_conversations_for_user(gRPCServer.conversationsCollection, authToken)
        # cursor = gRPCServer.conversationsCollection.changes([
        #     {'$match': {
        #         'operationType': {'$in': ['insert', 'replace']}
        #     }},
        #     {'$match': {
        #         'newDocument.n': {'$gte': 1}
        #     }}
        # ])
        try:
            obj = cursor.next()
            while obj:
                try:
                    conversation_view = other98_pb2.ConversationView()
                    conversation = chat.get_conversation_with_object_id(gRPCServer.conversationsCollection,
                                                                        obj['_id'], authToken)
                    if conversation:
                        conversation_view.conversation.CopyFrom(conversation)
                        conversation_view.id = str(obj['_id'])
                        result = other98_pb2.Result()
                        result.statusCode = 1
                        conversation_view.result.CopyFrom(result)
                        log_result(conversation_view, request_log)
                        yield conversation_view
                    obj = cursor.next()
                except StopIteration:
                    cursor = chat.get_conversations_change_stream_for_user(gRPCServer.conversationsCollection, user_handle=authToken)
                    try:
                        print(str(cursor))
                        obj = cursor.next()
                        while obj:
                            print(str(obj))
                            objectId = obj['fullDocument']['_id']
                            try:
                                conversation_view = other98_pb2.ConversationView()
                                conversation = chat.get_conversation_with_object_id(gRPCServer.conversationsCollection,
                                                                                    objectId, authToken)
                                if conversation:
                                    conversation_view.conversation.CopyFrom(conversation)
                                    conversation_view.id = str(objectId)
                                    result = other98_pb2.Result()
                                    result.statusCode = 1
                                    conversation_view.result.CopyFrom(result)
                                    log_result(conversation_view, request_log)
                                    yield conversation_view
                                obj = cursor.next()
                            except StopIteration:
                                break
                    except StopIteration:
                        print('waiting')
        except StopIteration:
            obj = None

    def GetConversation(self, request, context):
        request_log = log_get_request('get conversation', request, context)
        conversationId = request.value
        authToken = request.authToken
        # get username here when possible, for now auth token will be the username
        conversation_view = other98_pb2.ConversationView()
        result = other98_pb2.Result()
        conversation = chat.get_conversation_with_id_string(gRPCServer.conversationsCollection, conversationId, authToken)
        if conversation:
            result.statusCode = 1
            conversation_view.conversation.CopyFrom(conversation)
        else:
            result.statusCode = 4
            result.errorMessage = "Conversation not found"
        conversation_view.result.CopyFrom(result)
        log_result(conversation_view, request_log)
        return conversation_view

    def GetMessagesInConversation(self, request, context):
        request_log = log_get_request('get my conversations', request, context)
        conversationId = request.conversationId
        authToken = request.authToken
        # get username here when possible, for now auth token will be the username
        if chat.can_user_participate_in_conversation(gRPCServer.conversationsCollection, conversationId,
                                                     authToken):
            # first yield old messages
            current_messages = chat.get_current_messages_in_conversation(gRPCServer.conversationsCollection, gRPCServer.messagesCollection, conversationId, authToken)
            for message in current_messages:
                print(message)
                yield message

            # then subscribe to changes
            cursor = chat.get_message_change_stream_for_conversation(gRPCServer.messagesCollection, conversationId)
            for change in cursor:
                try:
                    # if chat.can_user_participate_in_conversation(gRPCServer.conversationsCollection, change['fullDocument']['conversationId'], authToken) \
                    #         and change['fullDocument']['senderHandle'] != authToken:
                    if chat.can_user_participate_in_conversation(gRPCServer.conversationsCollection,
                                                                 change['fullDocument']['conversationId'], authToken):
                        yield chat.get_message_view_with_object_id(gRPCServer.messagesCollection, change['fullDocument']['_id'])
                except StopIteration:
                    continue
        else:
            print('fuck off')

    def CreateConversation(self, request, context):
        # request_log = log_post_request("create conversation", request, context)
        authToken = request.authToken
        conversation = request.conversation
        # get creator handle using authToken. For now, authToken is the creator handle
        # perform validation on whether user is able to create conversations
        result = other98_pb2.Result()
        if authToken and authToken != '' and authToken != "":
            conversation.creatorHandle = authToken
            createdId = chat.create_conversation(gRPCServer.conversationsCollection, conversation.creatorHandle, conversation)
            if createdId and createdId != '' and createdId != "":
                result.statusCode = 1
                result.createdId = createdId
            else:
                result.statusCode = 5
                result.errorMessage = "An error unknown occurred while creating this conversation"
        # log_result(result, request_log)
        return result

    def SendMessage(self, request, context):
        # request_log = log_post_request("send message", request, context)
        authToken = request.authToken
        message = request.message
        result = other98_pb2.Result()
        # get creator handle using authToken. For now, authToken is the creator handle
        if chat.can_user_participate_in_conversation(gRPCServer.conversationsCollection, message.conversationId, authToken):
            message.createDate = util.current_milli_time()
            message.senderHandle = authToken
            createdId = chat.create_message_in_conversation(gRPCServer.conversationsCollection, gRPCServer.messagesCollection, message)
            if createdId and createdId != '' and createdId != "":
                result.createdId = createdId
                result.statusCode = 1
            else:
                result.statusCode = 5
                result.errorMessage = "An unknown error when sending the message"
        else:
            result.statusCode = 3
            result.errorMessage = "You are not allowed to participate in that conversation"
        return result

    def PopulateDatabase(self, request, context):
        gRPCServer.serverInstance.drop_database(name_or_database=gRPCServer.database_name)
        gRPCServer.theOther98Db = gRPCServer.serverInstance[gRPCServer.database_name]
        gRPCServer.profilesCollection = gRPCServer.theOther98Db[gRPCServer.profiles_collection_name]
        gRPCServer.postsCollection = gRPCServer.theOther98Db[gRPCServer.posts_collection_name]
        created_profiles = []
        for x in range(100):
            try:
                profile = other98_pb2.Profile()
                value = random_generator(8)
                profile.handle = value
                profile.email = value + '@' + value + '.com'
                profile.type = value
                create_profile(gRPCServer.profilesCollection, profile)
                if x % 20 == 0:
                    created_profiles.append(profile)
            except:
                continue
        for x in range(100000):
            try:
                post = other98_pb2.Post()
                value = random_generator(10)
                try:
                    author = created_profiles[x % 5]
                except:
                    author = None
                if author:
                    postsmallview = other98_pb2.PostSmallView()
                    postsmallview.title = value
                    postsmallview.description = value
                    postsmallview.type = value
                    postsmallview.authorHandle = author.handle
                    post.postSmallView.CopyFrom(postsmallview)

                    contentBlock = other98_pb2.ContentBlock()
                    contentBlock.content = value
                    contentBlock.type = x % 5
                    post.contentBlocks.extend([contentBlock])

                    posttags = []
                    roles_viewable = []
                    if x % 3 == 0:
                        posttags.append('news')
                        roles_viewable = [role_user]
                    elif x % 3 == 1:
                        posttags.append('forum')
                        roles_viewable = default_roles_viewable
                    elif x % 3 == 2:
                        posttags.extend(['news', 'forum'])
                        roles_viewable = default_roles_viewable
                    else:
                        posttags.append(['huh?'])

                    post.postTags.extend(posttags)

                    if post:
                        id = create_post(gRPCServer.postsCollection, post, roles_viewable)

                        if id:
                            # generate postvotes for feed testing
                            postVote = other98_pb2.PostVote()
                            postVote.userHandle = author.handle
                            postVote.postViewId = str(id)
                            postVote.voteValue = 1
                            vote_on_post(gRPCServer.postsCollection, postVote)

                        if id:
                            # now insert comments
                            commentvalue = random_generator(19)
                            comment = other98_pb2.Comment()
                            comment.postViewId = str(id)
                            comment.text = commentvalue
                            comment.contentBlocks.extend([])
                            for num in range(x % 3):
                                print(str(num))
                                try:
                                    create_comment(gRPCServer.postsCollection, comment)
                                except:
                                    continue
                else:
                    continue
            except:
                continue
        return other98_pb2.Void()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    other98_pb2_grpc.add_TheOther98Servicer_to_server(
        gRPCServer(), server)
    server.add_insecure_port('127.0.0.1:50051')
    server.start()
    try:
        while True:
            time.sleep(1)
            continue
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()