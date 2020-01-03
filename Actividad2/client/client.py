from __future__ import print_function
import logging
import socket
import threading
import time
import pika
import os
import uuid
import sys
import json
from datetime import datetime


class Client:

    def __init__(self):
        print("Iniciando conexión con RabbitMQ, por favor espere...")
        #time.sleep(10)

        self.client_uuid = uuid.uuid4()
        self.username = ""
        self.is_logged = False

        self.connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        self.channel = self.connection.channel()

    def _get_msgs(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()

        channel.exchange_declare(exchange='broadcast', exchange_type='fanout')

        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue

        channel.queue_bind(exchange='broadcast', queue=queue_name)

        def callback(ch, method, properties, body):
            message_received_string = body.decode("utf-8")
            message_received = json.loads(message_received_string)

            user = message_received["username"]
            text = message_received["message"]
            timestamp = message_received["timestamp"]

            print("[{}]: {}".format(user, text))
        
        channel.basic_consume(
            queue=queue_name, on_message_callback=callback, auto_ack=True)
        
        channel.start_consuming()
        
    def get_msgs(self):
        threading.Thread(target=self._get_msgs, daemon=True).start()

    def _get_direct_messages(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()

        result = channel.queue_declare(queue=str(self.client_uuid), exclusive=True)
        queue_name = result.method.queue

        channel.queue_bind(exchange='user_channel', queue=queue_name)

        def callback(ch, method, properties, body):
            server_response = body.decode("utf-8")
            server_response_json = json.loads(server_response)    
            response_type = server_response_json["type"]            
            response = server_response_json["response"]

            if response_type == "register":
                
                if response == "ok":
                    self.is_logged = True
                    print("Registro correcto")

                else:
                    self.is_logged = False
                    print("Usuario ya registrado")
                
                self.done_checking.set()

            elif response_type == "login":
                
                if response == "ok":
                    self.is_logged = True
                    print("Inicio correcto")

                else:
                    print("Credenciales inválidas")
                
                self.done_checking.set()

            elif response_type == "user_messages":
                for message in response:
                    print(message)

            elif response_type == "users_list":
                for user in response:
                    print(user)

            else:
                print("Problemas con el servidor")

        channel.basic_consume(
            queue=queue_name, on_message_callback=callback, auto_ack=True)

        channel.start_consuming()

    def get_direct_messages(self):
        threading.Thread(target=self._get_direct_messages, daemon=True).start()

    def send(self, message, option):
        now = datetime.now()
        timestamp = datetime.timestamp(now)

        if message != '':

            if option == "login":
                credentials = message

                message = {
                    'id': str(uuid.uuid4()),
                    'type': "login",
                    'username': credentials["username"],
                    'password': credentials["password"],
                    'client_uuid': str(self.client_uuid),
                    'timestamp': timestamp
                }

            elif option == "register":
                credentials = message

                message = {
                    'id': str(uuid.uuid4()),
                    'type': "register",
                    'username': credentials["username"],
                    'password': credentials["password"],
                    'client_uuid': str(self.client_uuid),
                    'timestamp': timestamp
                }

            elif option == "text":
                text = message
                
                message = {
                    'id': str(uuid.uuid4()),
                    'type': "message",
                    'username': self.username,
                    'client_uuid': str(self.client_uuid),
                    'message': text,
                    'timestamp': timestamp
                }

            elif option == "users_list":
                message = {
                    'id': str(uuid.uuid4()),
                    'type': "users_list",
                    'client_uuid': str(self.client_uuid),
                    'timestamp': timestamp
                }

            elif option == "user_messages":
                message = {
                    'id': str(uuid.uuid4()),
                    'type': "user_messages_list",
                    'username': self.username,
                    'client_uuid': str(self.client_uuid),
                    'timestamp': timestamp
                }

            body_message = json.dumps(message)

            self.channel.basic_publish(
                exchange='',
                routing_key='server_pending_messages',
                body=body_message,
                properties = pika.BasicProperties(content_type='text/plain', delivery_mode=2)
            )

    def connect(self, opt):

        if opt == 'login':
            request_type = "login"
            print("Iniciar sesión")
            print("-----------------------------")

        elif opt == "register":
            request_type = "register"
            print("Crear usuario")
            print("-----------------------------")

        self.done_checking = threading.Event()

        while not self.is_logged:
            username = input("Ingrese nombre de usuario: ")
            password = input("Ingrese contraseña: ")

            if username == "" or password == "":
                print("No puede ingresar campos vacíos")

            else:
                now = datetime.now()
                timestamp = datetime.timestamp(now)

                message = {
                    'username': username,
                    'password': password
                }

                self.send(message, request_type)
                self.done_checking.wait()
                self.done_checking.clear()

        self.username = username

if __name__ == '__main__':
    logging.basicConfig()
    client = Client()
    client.get_direct_messages()
    
    connected = False
    while not connected:
        print("Bienvenido a Chat No-RPC")
        print("1) Iniciar sesión")
        print("2) Registrar usuario")
        user_input = input("Escoja una opción: ")

        if user_input == '1':
            client.connect("login")
            connected = True

        elif user_input == '2':
            client.connect("register")
            connected = True

        else:
            print("Opción inválida")

    client.get_msgs()

    while True:
        user_input = input()
        sys.stdout.write("\033[F")

        # Comando para ver los clientes conectados al chat.
        if user_input == "/users":
            client.send(user_input, "users_list")

        # Comando para ver los mensajes enviados por el cliente.
        elif user_input == "/mymgs":
            client.send(user_input, "user_messages")

        # Comando para desconectarse del chat.
        elif user_input == "/exit":
            c.disconnect()
            break

        # Envío de un mensaje normal.
        else:
            client.send(user_input, "text")