from __future__ import print_function
import logging
import socket
import threading

import grpc

import protos.chat_pb2 as chat_pb2
import protos.chat_pb2_grpc as chat_pb2_grpc


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
            print("R[{}] {}".format(Msg.client_id, Msg.message))

    def send(self, dest_user, msg):
        if msg != '':
            chat_msg = chat_pb2.Msg()
            chat_msg.client_id = self.username
            chat_msg.dest_id = dest_user
            chat_msg.message = msg
            print("S[{}] {}".format(chat_msg.client_id, chat_msg.message))
            self.stub.SendMsg(chat_msg)
            #self.messages_stub.GetAllMessages(chat_pb2.Empty())
            self.messages_stub.SaveMessage(chat_msg)

    def get_users(self):
        print("Lista de usuarios conectados: ")
        users_list = self.users_stub.GetUsers(chat_pb2.Empty())
        
        for user in users_list.users:
            print(user.user_id)

    def get_user_messages(self):
        print("Lista de mensajes enviados: ")
        print("-----------------------------")
        user = chat_pb2.User()
        user.user_id = self.username
        user_messages = self.messages_stub.GetAllMessages(user)

        print(user_messages)
        for message in user_messages.msgs:
            print(message.message)


if __name__ == '__main__':
    logging.basicConfig()
    c = Client()

    while True:
        print("Elija una opción")
        print("----------------------------")
        print("1) Enviar mensaje")
        print("2) Recibir mensajes")
        print("3) Mostrar lista de usuarios")
        print("4) Mostrar todos mis mensajes enviados")
        opt = input("Su opción: ")

        if opt == '2':
            msg = input("Escriba su mensaje: ")
            c.send(c.username, msg)

        
        elif opt == '3':
            print("???")
            c.get_users()

        elif opt == '4':
            c.get_user_messages()

    #c.get_users()
    #c.JoinChat()
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