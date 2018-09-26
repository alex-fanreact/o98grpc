# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import other98_pb2 as other98__pb2


class TheOther98Stub(object):
  """The greeting service definition.
  """

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.GetFeed = channel.unary_stream(
        '/helloworld.TheOther98/GetFeed',
        request_serializer=other98__pb2.FeedRequest.SerializeToString,
        response_deserializer=other98__pb2.PostFeedView.FromString,
        )
    self.GetPost = channel.unary_unary(
        '/helloworld.TheOther98/GetPost',
        request_serializer=other98__pb2.Id.SerializeToString,
        response_deserializer=other98__pb2.PostView.FromString,
        )
    self.GetProfile = channel.unary_unary(
        '/helloworld.TheOther98/GetProfile',
        request_serializer=other98__pb2.Handle.SerializeToString,
        response_deserializer=other98__pb2.Profile.FromString,
        )
    self.CreatePost = channel.unary_unary(
        '/helloworld.TheOther98/CreatePost',
        request_serializer=other98__pb2.Post.SerializeToString,
        response_deserializer=other98__pb2.Result.FromString,
        )
    self.CreateComment = channel.unary_unary(
        '/helloworld.TheOther98/CreateComment',
        request_serializer=other98__pb2.Comment.SerializeToString,
        response_deserializer=other98__pb2.Result.FromString,
        )


class TheOther98Servicer(object):
  """The greeting service definition.
  """

  def GetFeed(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetPost(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetProfile(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def CreatePost(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def CreateComment(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_TheOther98Servicer_to_server(servicer, server):
  rpc_method_handlers = {
      'GetFeed': grpc.unary_stream_rpc_method_handler(
          servicer.GetFeed,
          request_deserializer=other98__pb2.FeedRequest.FromString,
          response_serializer=other98__pb2.PostFeedView.SerializeToString,
      ),
      'GetPost': grpc.unary_unary_rpc_method_handler(
          servicer.GetPost,
          request_deserializer=other98__pb2.Id.FromString,
          response_serializer=other98__pb2.PostView.SerializeToString,
      ),
      'GetProfile': grpc.unary_unary_rpc_method_handler(
          servicer.GetProfile,
          request_deserializer=other98__pb2.Handle.FromString,
          response_serializer=other98__pb2.Profile.SerializeToString,
      ),
      'CreatePost': grpc.unary_unary_rpc_method_handler(
          servicer.CreatePost,
          request_deserializer=other98__pb2.Post.FromString,
          response_serializer=other98__pb2.Result.SerializeToString,
      ),
      'CreateComment': grpc.unary_unary_rpc_method_handler(
          servicer.CreateComment,
          request_deserializer=other98__pb2.Comment.FromString,
          response_serializer=other98__pb2.Result.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'helloworld.TheOther98', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
