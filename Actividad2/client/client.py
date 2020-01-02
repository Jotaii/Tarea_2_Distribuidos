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

        self.connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        self.channel = self.connection.channel()

        self.channel.exchange_declare(exchange='user_channel', exchange_type='direct')

    def register(self):
        
        self.cont = True
        while self.cont:
            result = self.channel.queue_declare(queue=str(self.client_uuid), exclusive=True)
            queue_name = result.method.queue

            self.channel.queue_bind(exchange='user_channel', queue=queue_name)

            username = input("Ingrese un nombre de usuario: ")
            password = input("Ingrese una contraseña: ")

            message = {
                'type': "register",
                'username': username,
                'password': password,
                'uuid': str(self.client_uuid)
                }

            body_message = json.dumps(message)

            self.channel.basic_publish(
                exchange='',
                routing_key='server_pending_messages',
                body=body_message,
                properties = pika.BasicProperties(content_type='text/plain', delivery_mode=2)
            )

            def callback(ch, method, properties, body):

                if body.decode("utf-8") == "ok":
                    self.username = username
                    self.channel.basic_cancel(consumer_tag=str(self.client_uuid))
                    self.channel.queue_delete(queue=queue_name)
                    self.cont = False
                    print("Se ha registrado correctamente")
                
                else:
                    self.channel.basic_cancel(consumer_tag=str(self.client_uuid))
                    self.channel.queue_delete(queue=queue_name)
                    print("Usuario ya registrado")

            self.channel.basic_consume(
                queue=queue_name, on_message_callback=callback, auto_ack=True, consumer_tag=str(self.client_uuid))

            self.channel.start_consuming()

    def login(self):
        self.cont = True

        while self.cont:
            result = self.channel.queue_declare(queue=str(self.client_uuid), exclusive=True)
            queue_name = result.method.queue

            self.channel.queue_bind(exchange='user_channel', queue=queue_name)
            username = input("Ingrese un nombre de usuario: ")
            password = input("Ingrese su contraseña: ")

            now = datetime.now()
            timestamp = datetime.timestamp(now)

            request_json = {
                'id': str(uuid.uuid4()),
                'type': "login",
                'username': username,
                'password': password,
                'uuid': str(self.client_uuid),
                'timestamp': timestamp
                }

            request = json.dumps(request_json)

            self.channel.basic_publish(
                exchange='',
                routing_key='server_pending_messages',
                body=request,
                properties = pika.BasicProperties(content_type='text/plain', delivery_mode=2)
            )

            def callback(ch, method, properties, body):
                server_response_string = body.decode("utf-8")
                server_response_json = json.loads(server_response_string)

                if server_response_json["response"] == "ok":
                    self.username = username
                    self.channel.basic_cancel(consumer_tag=str(self.client_uuid))
                    self.channel.queue_delete(queue=queue_name)
                    self.cont = False
                    print("Logueado correctamente")
                
                else:
                    self.channel.basic_cancel(consumer_tag=str(self.client_uuid))
                    self.channel.queue_delete(queue=queue_name)
                    print("Credenciales inválidas o usuario ya logueado")

            self.channel.basic_consume(
                queue=queue_name, on_message_callback=callback, auto_ack=True, consumer_tag=str(self.client_uuid))

            self.channel.start_consuming()

    def _get_msgs(self):
        # VER SI SE PUEDE UNIFICAR EN 1 CHANNEL
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

            print("[{}]: {}".format(user, text))
        
        channel.basic_consume(
            queue=queue_name, on_message_callback=callback, auto_ack=True)
        
        channel.start_consuming()
        
    def get_msgs(self):
        threading.Thread(target=self._get_msgs, daemon=True).start()

    def send(self, msg):
        if msg != '':
            now = datetime.now()
            timestamp = datetime.timestamp(now)

            message = {
                'type': "message",
                'id': str(uuid.uuid4()),
                'username': self.username,
                'message': msg,
                'timestamp': timestamp
                }

            body_message = json.dumps(message)

            self.channel.basic_publish(
                exchange='',
                routing_key='server_pending_messages',
                body=body_message,
                properties = pika.BasicProperties(content_type='text/plain', delivery_mode=2)
            )
            

    #PENDIENTE
    def get_users(self):
        print("Lista de usuarios conectados: ")
        #users_list = self.users_stub.GetUsers(chat_pb2.Empty())
        
        #for user in users_list.users:
        #    print(user.user_id)


    def get_user_messages(self):

        def callback(ch, method, properties, body):
            print(" R[x] Received %r" % body)

        #Declaramos la cola denuevo (buena practica)
        self.channel.queue_declare(queue=self.username, durable=True)

        self.channel.queue_bind(exchange='broadcast', queue=self.username)

        

        print("Lista de mensajes enviados: ")
        print("-----------------------------")
        self.channel.basic_consume(queue=self.username,
                            auto_ack=True,
                            on_message_callback=callback)

        print(' [*] Waiting for messages. To exit press CTRL+C')
        self.channel.start_consuming()

    def disconnect(self):
        self.connection.close()

    

if __name__ == '__main__':
    logging.basicConfig()
    c = Client()

    print("1) Conectarse")
    print("2) Registrarse")
    user_input = input("Escoja una opción: ")

    if user_input == '1':
        c.login()
        c.get_msgs()

    elif user_input == '2':
        c.register()
        c.get_msgs()

    else:
        print("Opción inválida")

    # Comandos de usuario
    while True:
        user_input = input()
        sys.stdout.write("\033[F")

        # Comando para ver los clientes conectados al chat.
        if user_input == "/users":
            c.get_users()

        # Comando para ver los mensajes enviados por el cliente.
        elif user_input == "/mymessages":
            c.get_user_messages()

        # Comando para desconectarse del chat.
        elif user_input == "/exit":
            c.disconnect()
            break

        # Envío de un mensaje normal.
        else:
            c.send(user_input)