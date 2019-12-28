from __future__ import print_function
import logging
import socket
import threading

import grpc

import protos.chat_pb2 as chat_pb2
import protos.chat_pb2_grpc as chat_pb2_grpc

import sys


class Client:

    def __init__(self):

        channel = grpc.insecure_channel('server:50051')
        self.users_stub = chat_pb2_grpc.UsersStub(channel)
        request = chat_pb2.User()

        exit = False
        while exit == False:
            username = input("Ingrese nombre de usuario: ")
            request.user_id = username
            response = self.users_stub.Join(request)

            if response.opt:
                print("Logueado correctamente")
                self.username = username
                exit = True

            else:
                print("Nombre de usuario no disponible. Ingrese otro nombre de usuario")
        
        self.stub = chat_pb2_grpc.ChatStub(channel)
        self.messages_stub = chat_pb2_grpc.MessagesServiceStub(channel)
        threading.Thread(target=self.get_msgs, daemon=True).start()

    def get_msgs(self):
        for Msg in self.stub.Channel(chat_pb2.Empty()):
            print("[{}] {}".format(Msg.client_id, Msg.message))
        
    def send(self, dest_user, msg):
        if msg != '':
            chat_msg = chat_pb2.Msg()
            chat_msg.client_id = self.username
            chat_msg.dest_id = dest_user
            chat_msg.message = msg
            #print("S[{}] {}".format(chat_msg.client_id, chat_msg.message))
            self.stub.SendMsg(chat_msg)
            self.messages_stub.SaveMessage(chat_msg)

    def get_users(self):
        print("------------------------------")
        print("Lista de usuarios conectados: ")
        users_list = self.users_stub.GetUsers(chat_pb2.Empty())
        
        for user in users_list.users:
            print(user.user_id)

        print("------------------------------")

    def get_user_messages(self):
        print("------------------------------")
        print("Lista de mensajes enviados: ")
        user = chat_pb2.User()
        user.user_id = self.username
        user_messages = self.messages_stub.GetAllMessages(user)

        print(user_messages)
        for message in user_messages.msgs:
            print(message.message)

        print("------------------------------")

if __name__ == '__main__':
    logging.basicConfig()
    c = Client()

    while True:
        #input_text = "[" + c.username + "] "
        #user_input = input(input_text)
        user_input = input()
        sys.stdout.write("\033[F")

        if user_input == "/users":
            c.get_users()

        elif user_input == "/mymessages":
            c.get_user_messages()

        elif user_input == "/exit":
            break

        else:
            c.send(c.username, user_input)
