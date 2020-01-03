from __future__ import print_function
import logging
import socket
import threading

import grpc

import chat_pb2 as chat_pb2
import chat_pb2_grpc as chat_pb2_grpc

import sys
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime


class Client:
    """
    Clase Cliente que se conecta al chat mediante protocolos RPC. 
    
    Permite el envío de mensajes y obtención de listas mediante el
    el framework gRPC.
    """
    def __init__(self):
        # Conexión con el servidor mediante un channel inseguro.
        channel = grpc.insecure_channel('server:50051')
        
        # Stub para el servicio de Chat. 
        self.users_stub = chat_pb2_grpc.UsersStub(channel)

        # Creación de un mensaje tipo User para la autenticación al chat.
        request = chat_pb2.User()

        exit = False
        while exit == False:
            username = input("Ingrese nombre de usuario: ")
            
            if (username == '') or (' ' in username) or ('/' in username):
                print("No se pueden dejar espacios ni usar el caracter /") 

            else:
                request.user_id = username
                response = self.users_stub.Join(request)

                if response.opt:
                    # Almacenamiento del ID único del cliente en el servidor.
                    print("Logueado correctamente")
                    print("------------------------------\n")
                    self.username = username
                    exit = True

                else:
                    print("Nombre de usuario no disponible\n")
        
        # Stubs para servicios de Mensajería y Usuarios.
        self.stub = chat_pb2_grpc.ChatStub(channel)
        self.messages_stub = chat_pb2_grpc.MessagesServiceStub(channel)

        # Thread para monitoreo constante de mensajes recibidos.
        threading.Thread(target=self.get_msgs, daemon=True).start()

    def get_msgs(self):
        """
        Un método para el monitoreo de mensajes.

        Permite monitorear constantemente sin alterar la interacción del usuario (asincronía)
        mediante un thread que ejecuta la función paralelamente.
        """
        for Msg in self.stub.Channel(chat_pb2.Empty()):
            username = Msg.id.split("/")[0]
            seconds = Msg.timestamp.seconds
            dt_object = datetime.fromtimestamp(seconds)
            date_time = dt_object.strftime("%m/%d/%Y, %H:%M:%S")
            print("[{} - {} ] {}".format(date_time, username, Msg.message))
        
    def send(self, msg):
        """
        Un método para el envío de mensajes.

        Permite el envío de un mensaje escrito por el cliente. La ejecución de esta función
        envía el mensaje al servidor para su re-envío y almacenamiento.
        """
        if msg != '':
            timestamp = Timestamp()
            timestamp.GetCurrentTime()
            msg_id = self.username + "/" + str(timestamp.nanos)
            
            chat_msg = chat_pb2.Msg()
            chat_msg.id = msg_id
            chat_msg.message = msg
            chat_msg.timestamp.seconds = timestamp.seconds
            #chat_msg.timestamp.nanos = timestamp.nanos
            
            self.stub.SendMsg(chat_msg)
            self.messages_stub.SaveMessage(chat_msg)

    def get_users(self):
        """
        Un método para obtener la lista de usuarios desde el servidor.

        A través del stub, el cliente mediante un mensaje vacío recibe un mensaje que contiene
        una lista con todos los usuarios conectados al chat.
        """
        print("\n\n------------------------------")
        print("Lista de usuarios conectados: ")
        print("------------------------------")
        users_list = self.users_stub.GetUsers(chat_pb2.Empty())
        
        for user in users_list.users:
            print(user.user_id)

        print("")

    def get_user_messages(self):
        """
        Un método para obtener la lista de mensajes envíados por el cliente.

        Al igual que la función para la obtención de usuarios, el cliente recibe un mensaje que
        contiene una lista con todos los mensajes enviados por éste.
        """
        print("\n\n------------------------------")
        print("Lista de mensajes enviados ")
        print("------------------------------")
        user = chat_pb2.User()
        user.user_id = self.username
        user_messages = self.messages_stub.GetAllMessages(user)

        for message in user_messages.msgs:
            username = message.id.split("/")[0]
            seconds = message.timestamp.seconds
            dt_object = datetime.fromtimestamp(seconds)
            date_time = dt_object.strftime("%m/%d/%Y, %H:%M:%S")
            print("[{} - {} ] {}".format(date_time, username, message.message))

        print("")

    def disconnect(self):
        """
        Un método para desconectar al cliente del chat.

        Mediante el stub, el envío de un mensaje de usuario permite que el servidor borre el id de
        éste de los usuarios conectados al chat y todos sus mensajes.
        """
        user = chat_pb2.User()
        user.user_id = self.username

        self.messages_stub.DeleteMessages(user)
        self.users_stub.Disconnect(user)


if __name__ == '__main__':
    logging.basicConfig()
    print("\n-----------------------------")
    print("Bienvenido al Chat RPC")
    print("Un chat donde los RPC son bienvenidos")
    c = Client()

    print("-----------------------------")
    print("INFORMACIÓN")
    print("-----------------------------")
    print("Se ha conectado al chat como " + c.username)
    print("Para enviar un mensaje simplemente escriba y presione enter\n")
    print("Algunos comandos de utilidad:")
    print("/users: Lista los usuarios conectados")
    print("/mymgs: Lista sus mensajes enviados")
    print("/exit: Abandonar chat (o puede usar Ctrl+C directamente)\n")

    # Comandos de usuario
    while True:
        try:
            user_input = input()
            sys.stdout.write("\033[F")

            # Comando para ver los clientes conectados al chat.
            if user_input == "/users":
                c.get_users()

            # Comando para ver los mensajes enviados por el cliente.
            elif user_input == "/mymgs":
                c.get_user_messages()

            # Comando para desconectarse del chat.
            elif user_input == "/exit":
                c.disconnect()
                break

            # Envío de un mensaje normal.
            else:
                c.send(user_input)
        except KeyboardInterrupt:
            c.disconnect()
            break
    print("Sesión cerrada. ¡Hasta pronto!")