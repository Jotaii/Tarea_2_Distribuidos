from concurrent import futures
import logging

import grpc

import protos.chat_pb2 as chat_pb2
import protos.chat_pb2_grpc as chat_pb2_grpc


class Chat(chat_pb2_grpc.ChatServicer):

    def __init__(self):
        self.chats = []

    def SendMsg(self, request: chat_pb2.Msg, context):
        self.chats.append(request)
        return chat_pb2.Empty()
        #return chat_pb2.SendMsg(message="Hola, %s!" % request.name)

    def Channel(self, request, context):
        lastindex = 0
        while True:
            while len(self.chats) > lastindex:
                n = self.chats[lastindex]
                lastindex += 1
                yield n
    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServicer_to_server(Chat(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    serve()
