"""The Python implementation of the gRPC route guide client."""

import grpc

import other98_pb2
import other98_pb2_grpc


def get_profile(stub, handle: str):
    return stub.GetProfile(other98_pb2.GetRequest(value=handle))


def get_feed(stub, postTags: [str], page_id:str='', page_size:int=20, handle: str=''):
    request = other98_pb2.FeedRequest()
    request.postTags.extend(postTags)
    request.pageId = page_id
    request.pageSize = page_size
    request.authToken = handle
    return stub.GetFeed(request)


def populate_database(stub):
    return stub.PopulateDatabase(other98_pb2.Void())


def create_post(stub, postSmallView: other98_pb2.PostSmallView, contentBlocks: [other98_pb2.ContentBlock], postTags: [str], viewable_permissions: [str]=None):
    post = other98_pb2.Post()
    post.postSmallView.CopyFrom(postSmallView)

    post.contentBlocks.extend(contentBlocks)
    post.postTags.extend(postTags)

    create_post_request = other98_pb2.CreatePostRequest()
    create_post_request.post = post
    if viewable_permissions:
        create_post_request.viewable_roles.extend(viewable_permissions)
    return stub.CreatePost(create_post_request)


def create_comment(stub, comment: other98_pb2.Comment):
    if comment:
        return stub.CreateComment(comment)


def get_post(stub, idstring: str, userhandle: str):
    getRequest = other98_pb2.GetRequest()
    getRequest.value = idstring
    getRequest.authToken = userhandle
    return stub.GetPost(getRequest)


def vote_on_post(stub, user_handle: str, postview_id_string: str, vote_value: int):
    postvote = other98_pb2.PostVote()
    postvote.postViewId = postview_id_string
    postvote.userHandle = user_handle
    postvote.voteValue = vote_value
    return stub.VoteOnPost(postvote)


def create_conversation(stub, user_handle: str, participant_handles: [str], conversationName: str, isPrivate: bool):
    create_conversation_request = other98_pb2.CreateConversationRequest()
    create_conversation_request.authToken = user_handle
    conversation = other98_pb2.Conversation()
    for handle in participant_handles:
        conversation.participantHandles.extend([handle])
    conversation.conversationName = conversationName
    conversation.isPrivate = isPrivate
    create_conversation_request.conversation.CopyFrom(conversation)
    return stub.CreateConversation(create_conversation_request)


def create_message(stub, user_handle: str, conversationId: str, messageText: str):
    send_message_request = other98_pb2.SendMessageRequest()
    send_message_request.authToken = user_handle
    message = other98_pb2.Message()
    message.text = messageText
    message.conversationId = conversationId
    send_message_request.message.CopyFrom(message)
    return stub.SendMessage(send_message_request)


def get_my_conversations(stub, user_handle: str):
    get_request = other98_pb2.GetRequest()
    get_request.authToken = user_handle
    return stub.GetMyConversations(get_request)


def get_messages_in_conversation(stub, user_handle: str, conversationId: str):
    get_request = other98_pb2.GetRequest()
    get_request.authToken = user_handle
    get_request.value = conversationId
    return stub.GetMessagesInConversation(get_request)


def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = other98_pb2_grpc.TheOther98Stub(channel)
        print("-------------- GetProfile --------------")
        print(get_profile(stub, 'avi'))
        print("-------------- GetFeed: Forum --------------")
        print(get_feed(stub, ['forum']))
        print("-------------- GetFeed: News --------------")
        print(get_feed(stub, ['news']))
        return stub


if __name__ == '__main__':
    run()