import time
from concurrent import futures

import grpc

import other98_pb2 as other98_pb2
import other98_pb2_grpc as other98_pb2_grpc

class gRPCServer(other98_pb2_grpc.TheOther98Servicer):
    def __init__(self):
        print('init')
    
    def GetFeed(self, request, context):
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