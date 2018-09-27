"""The Python implementation of the gRPC route guide client."""

import grpc

import other98_pb2
import other98_pb2_grpc


def get_profile(stub, handle: str):
    return stub.GetProfile(other98_pb2.Handle(value=handle))


def get_feed(stub, postTags: [str], page_id:str='', page_size:int=20):
    request = other98_pb2.FeedRequest()
    request.postTags.extend(postTags)
    request.pageId = page_id
    request.pageSize = page_size
    return stub.GetFeed(request)


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


if __name__ == '__main__':
    run()