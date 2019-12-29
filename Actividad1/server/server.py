from concurrent import futures
import logging

import grpc

import protos.chat_pb2 as chat_pb2
import protos.chat_pb2_grpc as chat_pb2_grpc
from datetime import datetime


class Chat(chat_pb2_grpc.ChatServicer):

    def __init__(self):
        self.chats = []

    def SendMsg(self, request: chat_pb2.Msg, context):
        f = open("log.txt", "a")
        seconds = request.timestamp.seconds
        dt_object = datetime.fromtimestamp(seconds)
        date_time = dt_object.strftime("%m/%d/%Y, %H:%M:%S")
        f.write("[{} - {} ] {}\n".format(date_time, request.client_id, request.message))
        f.close()
        self.chats.append(request)

        return chat_pb2.Empty()

    def Channel(self, request, context):
        lastindex = 0
        while True:
            while len(self.chats) > lastindex:
                n = self.chats[lastindex]
                lastindex += 1
                yield n

class Users(chat_pb2_grpc.UsersServicer):
    
    def __init__(self):
        self.users = []

    def Join(self, request, context):
        response = chat_pb2.Response()
        
        if request.user_id in self.users:
            response.opt = False
            return response

        response.opt = True
        self.users.append(request.user_id)
        return response

    def GetUsers(self, request, context):
        users_list = chat_pb2.UsersListResponse()
        users_message = []

        for user in self.users:
            user_message = chat_pb2.User()
            user_message.user_id = user
            users_message.append(user_message)

        users_list.users.extend(users_message)

        return users_list

class MessagesServices(chat_pb2_grpc.MessagesServiceServicer):

    def __init__(self):
        self.user_messages = {}

    def SaveMessage(self, request, context):
        username = request.client_id

        if username not in self.user_messages:
            self.user_messages[username] = [request]

        else:
            self.user_messages[username].append(request)

        return chat_pb2.Empty()

    def GetAllMessages(self, request, context):
        username = request.user_id
        user_messages = chat_pb2.UserMessages()

        if username not in self.user_messages:
            return user_messages

        user_messages.msgs.extend(self.user_messages[username])
        return user_messages
        

def serve():
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
