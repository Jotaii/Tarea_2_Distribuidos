from datetime import datetime
from concurrent import futures
import logging

import grpc

import chat_pb2 as chat_pb2
import chat_pb2_grpc as chat_pb2_grpc

from google.protobuf.timestamp_pb2 import Timestamp


class Chat(chat_pb2_grpc.ChatServicer):
    """
    Clase Chat que define el servicio de chat.

    Permite el servicio de envío y recepción de mensajes entre clientes, como también
    registro de mensajes envíados, administración de usuarios y almacenamiento temporal
    de mensajes.
    """
    def __init__(self):
        # Definición de una lista intermediaria para el almacenamiento y envío de mensajes
        # del chat.
        self.chats = []

    def SendMsg(self, request: chat_pb2.Msg, context):
        """
        Un método que permite el envío de un mensaje entre cliente-servidor y viceversa.
        La ejecución de este método transporta el mensaje escrito por un cliente mediante 
        stubs. Además, registra en un archivo todos los mensajes que se han enviado.
        """
        timestamp = Timestamp()
        timestamp.GetCurrentTime()

        username = request.id.split("/")[0]
        # Se reemplaza el timestamp del cliente por el del server
        # para mantener consistencia con los tiempos
        client_seconds = request.timestamp.seconds
        server_seconds = timestamp.seconds

        dt_object_client = datetime.fromtimestamp(client_seconds)
        date_time_client = dt_object_client.strftime("%m/%d/%Y, %H:%M:%S")
        dt_object_server = datetime.fromtimestamp(server_seconds)
        date_time_server = dt_object_server.strftime("%m/%d/%Y, %H:%M:%S")

        f = open("log.txt", "a")
        #f.write("[{} - {} ] {}\n".format(date_time, username, request.message))
        f.write("\nRegistro de mensaje: \n")
        f.write("ID Mensaje: " + request.id + "\n")
        f.write("ID Cliente: " + username + "\n") 
        f.write("Mensaje: " + request.message + "\n")
        f.write("Fecha de envio en cliente: " + date_time_client + "\n")
        f.write("Fecha recepcion en server: " + date_time_server +"\n")
        f.close()

        self.chats.append(request)

        return chat_pb2.Empty()

    def Channel(self, request, context):
        """
        Un método que permite el flujo de mensajes. Permite que el servidor pueda mandar
        mensajes. Todos los clientes deben abrir esta conexión y esperar a que el servidor 
        envíe nuevos mensajes.
        """
        lastindex = 0
        while True:
            # Revisión de nuevos mensajes
            while len(self.chats) > lastindex:
                n = self.chats[lastindex]
                lastindex += 1
                yield n

class Users(chat_pb2_grpc.UsersServicer):
    """
    Una clase que define el servicio de Usuarios.

    Almacenamiento de los IDs de usuarios conectados al chat, permitiendo la conexión de 
    nuevos sin asignar IDs ya utilizadas. Además permite mostrar al usuario que lo solicite
    una lista de todos los clientes conectados al chat.
    """
    def __init__(self):
        self.users = []

    def Join(self, request, context):
        """
        Un método para asignar y almacenar los IDs de los clientes conectados.
        """
        response = chat_pb2.Response()
        
        if request.user_id in self.users:
            response.opt = False
            return response

        response.opt = True
        self.users.append(request.user_id)

        return response

    def GetUsers(self, request, context):
        """
        Un método que retorna la lista de los clientes conectados al chat.
        """
        users_list = chat_pb2.UsersListResponse()
        users_message = []

        for user in self.users:
            user_message = chat_pb2.User()
            user_message.user_id = user
            users_message.append(user_message)

        users_list.users.extend(users_message)

        return users_list

    def Disconnect(self, request, context):
        """
        Un método que permite la desconexión de un cliente en el chat. Borra el ID del 
        cliente almacenado.
        """
        username = request.user_id
        self.users.remove(username)

        return chat_pb2.Empty()

class MessagesServices(chat_pb2_grpc.MessagesServiceServicer):
    """
    Una Clase que define el servicio de Mensajes.

    Permite almacenar temporalmente los mensajes enviados por los clientes.
    """

    def __init__(self):
        self.user_messages = {}

    def SaveMessage(self, request, context):
        """
        Un método que almacena los mensajes con información de los mensajes enviados por clientes.
    
        Mediante un diccionario, guarda ordenadamente los mensajes según el ID del cliente que lo
        envió.
        """
        username = request.id.split("/")[0]

        if username not in self.user_messages:
            self.user_messages[username] = [request]

        else:
            self.user_messages[username].append(request)

        return chat_pb2.Empty()

    def GetAllMessages(self, request, context):
        """
        Un método que envía al cliente una lista con todos los mensajes que ha enviado.
        """
        username = request.user_id
        user_messages = chat_pb2.UserMessages()

        if username not in self.user_messages:
            return user_messages

        user_messages.msgs.extend(self.user_messages[username])
        return user_messages

    def DeleteMessages(self, request, context):
        """
        Un método que elimina todos los mensajes almacenados por el usuario que solicitó la desconexión.
        """
        username = request.user_id
        
        self.user_messages.pop(username, None)

        return chat_pb2.Empty()


def serve():
    """
    Una función que crea el gRPC server en un thread y conecta los servicios (Chat, Usuarios y 
    mensajería) al server. Finalmente el servidor abre un puerto inseguro y se ejecuta indeter-
    minadamente.
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_ChatServicer_to_server(Chat(), server)
    chat_pb2_grpc.add_UsersServicer_to_server(Users(), server)
    chat_pb2_grpc.add_MessagesServiceServicer_to_server(MessagesServices(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    logging.basicConfig()
    serve()
