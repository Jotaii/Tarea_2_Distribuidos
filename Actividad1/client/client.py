from __future__ import print_function
import logging
import socket
import threading

import grpc

import protos.chat_pb2 as chat_pb2
import protos.chat_pb2_grpc as chat_pb2_grpc

class Client:

    def __init__(self):
        self.username = input("Ingrese nombre de usuario: ")
        channel = grpc.insecure_channel('server:50051')
        self.stub = chat_pb2_grpc.ChatStub(channel)
        threading.Thread(target=self.__get_msgs, daemon=True).start()

    def __get_msgs(self):
        for Msg in self.stub.Channel(chat_pb2.Empty()):
            print("R[{}] {}".format(Msg.client_id, Msg.message))

    def send(self, dest_user, msg):
        if msg != '':
            chat_msg = chat_pb2.Msg()
            chat_msg.client_id = self.username
            chat_msg.dest_id = dest_user
            chat_msg.message = msg
            print("S[{}] {}".format(chat_msg.client_id, chat_msg.message))
            # response = stub.SendMsg(chat_pb2.SendMsg(name=client_name, message=msg))
            self.stub.SendMsg(chat_msg)

if __name__ == '__main__':
    logging.basicConfig()
    #client = Client()
    #client.send("hola")
    #run()

    '''        
def run():
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel('server:50051') as channel:
        client_name = socket.gethostname()
        stub = chat_pb2_grpc.ChatStub(channel)
        threading.Thread(target=self.get_msgs, daemon=True).start()

        response = stub.SendMsg(chat_pb2.SendMsg(name=client_name, message=msg))
    print("Greeter client received: " + response.message)
'''