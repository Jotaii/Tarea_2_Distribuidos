from __future__ import print_function
import logging
import socket
import threading
import time
import pika
import os
import uuid
import sys

class Client:

    def __init__(self):
        print("Iniciando conexión con RabbitMQ, por favor espere...")
        #time.sleep(10)
        self.username = input("Ingrese nombre de usuario: ")

        # username logic

        self.connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        self.channel = self.connection.channel()
    
        self.channel.exchange_declare(exchange='user_channel', exchange_type='direct')

    def _get_msgs(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()

        channel.exchange_declare(exchange='broadcast', exchange_type='fanout')

        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue

        channel.queue_bind(exchange='broadcast', queue=queue_name)

        def callback(ch, method, properties, body):
            print(" R[x] Received %r" % body)
        
        channel.basic_consume(
            queue=queue_name, on_message_callback=callback, auto_ack=True)
        
        channel.start_consuming()
        
    def get_msgs(self):
        threading.Thread(target=self._get_msgs, daemon=True).start()

    def send(self, msg):
        if msg != '':
            client_producer = self.username
            
            self.channel.basic_publish(
                exchange='',
                routing_key='server_pending_messages',
                body=msg,
                properties = pika.BasicProperties(content_type='text/plain', delivery_mode=2)
            )
                
            print(" [x] Sent 'Hello World!'")
            #self.connection.close()

    
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
    c.get_msgs()

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