import grpc
import pymongo
from bson.objectid import ObjectId
import other98_pb2 as other98_pb2
import other98_pb2_grpc as other98_pb2_grpc
import util


def get_message_view_after_message(collection: pymongo.collection, conversation_id: str, after_id: str= '') -> other98_pb2.MessageView:
    message_view = other98_pb2.MessageView()
    if conversation_id and conversation_id != '' and conversation_id != "":
        if after_id and after_id != '' and after_id != "":
            obj = collection.find_one({'$and': [{'conversationId': conversation_id},
                                                {'_id': {'$gt': ObjectId(after_id)}}]}).sort(
                [('createDate', pymongo.ASCENDING)])
        else:
            obj = collection.find({'conversationId': conversation_id}).sort(
                [('createDate', pymongo.ASCENDING)])

        message = util.parse_message(obj)
        message_view.id = str(obj['_id'])
        if message:
            message_view.message.CopyFrom(message)
    return message_view


def get_message_view_with_object_id(collection: pymongo.collection, message_id: ObjectId) -> other98_pb2.MessageView:
    message_view = other98_pb2.MessageView()
    if message_id:
        obj = collection.find_one({'_id': message_id})
        if obj:
            message = util.parse_message(obj)
            if message:
                message_view.id = str(obj['_id'])
                message_view.message.CopyFrom(message)
    return message_view


def get_message_view_with_id_string(collection: pymongo.collection, message_id: str) -> other98_pb2.MessageView:
    message_view = other98_pb2.MessageView()
    if message_id:
        obj = collection.find_one({'_id': ObjectId(message_id)})
        if obj:
            message = util.parse_message(obj)
            if message:
                message_view.id = str(obj['_id'])
                message_view.message.CopyFrom(message)
    return message_view


def get_current_messages_in_conversation(conversations_collection: pymongo.collection, messages_collection: pymongo.collection, conversation_id: str, user_handle: str):
    messages = []
    conversation = get_conversation_with_id_string(conversations_collection, conversation_id, user_handle)
    if conversation:
        cursor = messages_collection.find({'conversationId': conversation_id})
        try:
            obj = cursor.next()
            print('message is ' + str(obj))
            while obj:
                messageview = get_message_view_with_object_id(messages_collection, obj['_id'])
                messages.append(messageview)
                obj = cursor.next()
        except StopIteration:
            return messages
    return messages


def get_message_change_stream_for_conversation(messages_collection: pymongo.collection, conversation_id: str) -> pymongo.collection.CollectionChangeStream:
    if conversation_id and conversation_id != '' and conversation_id != "":
        return messages_collection.watch([{'$match': {'operationType': 'insert'}}])
    return None


def create_message_in_conversation(conversations_collection: pymongo.collection, messages_collection: pymongo.collection, message: other98_pb2.Message) -> str:
    if message and message.conversationId and message.conversationId != '' and message.conversationId != "":
        if can_user_participate_in_conversation(conversations_collection, message.conversationId, message.senderHandle):
            return str(messages_collection.insert_one(util.parse_to_document(message)).inserted_id)
        return None


def get_conversation_with_id_string(collection: pymongo.collection, idstring: str, user_handle: str) -> other98_pb2.Conversation:
    if idstring and idstring != '' and idstring != "":
        raw = collection.find_one({'$and': [{'participantHandles': {'$in': [user_handle]}},
                                            {'_id': ObjectId(idstring)}]})
        if raw is None:
            return None
        conversation = util.parse_conversation(raw)
        return conversation
    return None


def get_conversation_with_object_id(collection: pymongo.collection, object_id: ObjectId, user_handle: str) -> other98_pb2.Conversation:
    if id:
        raw = collection.find_one({'$and': [{'participantHandles': {'$in': [user_handle]}},
                                            {'_id': object_id}]})
        if raw is None:
            return None
        conversation = util.parse_conversation(raw)
        return conversation
    return None


def get_conversations_change_stream_for_user(conversations_collection: pymongo.collection, user_handle: str) -> pymongo.collection.CollectionChangeStream:
    if user_handle and user_handle != '' and user_handle != "":
        return conversations_collection.watch([{'$match': {'operationType': 'insert'}}])
    return None


def get_current_conversations_for_user(conversations_collections: pymongo.collection, user_handle: str):
    return conversations_collections.find({'participantHandles': {'$in': [user_handle]}})


def can_user_participate_in_conversation(conversations_collection, conversation_id: str, user_handle: str) -> bool:
    # conversation = get_conversation_with_id_string(conversations_collection, conversation_id, user_handle)
    raw = conversations_collection.find_one({'_id': ObjectId(conversation_id)})
    if raw is None:
        return False
    conversation = util.parse_conversation(raw)
    if conversation.isPrivate:
        for handle in conversation.participantHandles:
            if handle == user_handle:
                return True
    else:
        return True
    return False


def create_conversation(conversations_collection: pymongo.collection, creator_handle: str, conversation: other98_pb2.Conversation) -> str:
    # you have to validate the ability of this user to create a conversation before calling this method
    if creator_handle and creator_handle != '' and creator_handle != "" and conversation:
        return str(conversations_collection.insert_one(util.parse_to_document(conversation)).inserted_id)
    return None