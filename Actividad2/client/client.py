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
        time.sleep(5)

        self.client_uuid = uuid.uuid4()
        self.username = ""
        self.is_logged = False

        self.connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq', heartbeat=0))
        self.channel = self.connection.channel()

    def _get_msgs(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq', heartbeat=0))
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
            dt_object = datetime.fromtimestamp(timestamp)
            date_time = dt_object.strftime("%m/%d/%Y, %H:%M:%S")

            print("[{} - {}]: {}".format(date_time, user, text))
        
        channel.basic_consume(
            queue=queue_name, on_message_callback=callback, auto_ack=True,
            consumer_tag=self.username)
        
        channel.start_consuming()
        
    def get_msgs(self):
        threading.Thread(target=self._get_msgs, daemon=True).start()

    def _get_direct_messages(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq', heartbeat=0))
        channel = connection.channel()

        result = channel.queue_declare(queue=str(self.client_uuid), exclusive=True)
        queue_name = result.method.queue

        channel.queue_bind(exchange='user_channel', queue=queue_name)

        def callback(ch, method, properties, body):
            server_response = body.decode("utf-8")
            server_response_json = json.loads(server_response)    
            response_type = server_response_json["type"]            
            response = server_response_json["response"]

            if response_type == "login":
                
                if response == "ok":
                    self.is_logged = True
                    print("Inicio correcto. ¡Comience a chatear!")

                else:
                    print("Nombre de usuario ocupado\n")
                
                self.done_checking.set()

            elif response_type == "user_messages":
                print("\n\n-----------------------------")
                print("Mensajes enviados")
                print("-----------------------------")

                for sent_message in response:
                    message = json.loads(sent_message)

                    user = message["username"]
                    text = message["message"]
                    timestamp = message["timestamp"]
                    dt_object = datetime.fromtimestamp(timestamp)
                    date_time = dt_object.strftime("%m/%d/%Y, %H:%M:%S")

                    print("[{} - {}]: {}".format(date_time, user, text))
                print("")


            elif response_type == "users_list":
                print("\n\n-----------------------------")
                print("Lista de usuarios")
                print("-----------------------------")
                for user in response:
                    print(user)
                print("")
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
                    'username': credentials,
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
                    'username': self.username,
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

            elif option == "disconnect":
                message = {
                    'id': str(uuid.uuid4()),
                    'type': "disconnect",
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

    def connect(self):
        self.done_checking = threading.Event()

        while not self.is_logged:
            username = input("Ingrese nombre de usuario: ")

            if (username == "") or ('' in username == True):
                print("No puede ingresar campos vacíos")

            else:
                self.send(username, "login")
                self.done_checking.wait()
                self.done_checking.clear()

        self.username = username

    def disconnect(self):
        self.send("disconnect", "disconnect")
        self.connection.close()

if __name__ == '__main__':
    logging.basicConfig()
    client = Client()

    client.get_direct_messages()

    print("\n-----------------------------")
    print("Bienvenido al Chat No-RPC")
    print("Un chat donde los RPC no son bienvenidos")
    client.connect()

    print("-----------------------------\n")

    print("-----------------------------")
    print("INFORMACIÓN")
    print("-----------------------------")
    print("Se ha conectado al chat como " + client.username)
    print("Para enviar un mensaje simplemente escriba y presione enter\n")
    print("Algunos comandos de utilidad:")
    print("/users: Lista los usuarios conectados")
    print("/mymgs: Lista sus mensajes enviados")
    print("/exit: Abandonar chat (o puede usar Ctrl+C directamente)\n")
    
    client.get_msgs()

    while True:
        try:
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
                client.disconnect()
                break

            # Envío de un mensaje normal.
            else:
                client.send(user_input, "text")

        except KeyboardInterrupt:
            client.disconnect()
            break

    print("\n\nCerrando conexión... ¡Hasta pronto!")