from __future__ import print_function
import logging
import socket

import grpc

import protos.chat_pb2 as chat_pb2
import protos.chat_pb2_grpc as chat_pb2_grpc


def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('server:50051') as channel:
        stub = chat_pb2_grpc.ChatServerStub(channel)
        client_name = socket.gethostname()
        response = stub.SendMsg(chat_pb2.ClientRequest(name=client_name))
    print("Greeter client received: " + response.message)


if __name__ == '__main__':
    logging.basicConfig()
    run()