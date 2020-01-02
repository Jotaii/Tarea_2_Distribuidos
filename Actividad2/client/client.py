from __future__ import print_function
import logging
import socket
import threading
import time
import pika
import os
import uuid

class Client:

    def __init__(self):
        print("Iniciando conexión con RabbitMQ, por favor espere...")
        #time.sleep(10)

        self.connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        self.channel = self.connection.channel()
        self.username = "test"

        self.channel.queue_declare(queue=self.username, durable=True)
        self.channel.exchange_declare(exchange='user_channel', exchange_type='direct')

        threading.Thread(target=self.get_msgs, daemon=True).start()
    
    def get_msgs(self):
        self.channel.exchange_declare(exchange='broadcast', exchange_type='fanout')

        #Declaramos la cola denuevo (buena practica)
        result = self.channel.queue_declare(queue=self.username, durable=True)
        queue_name = result.method.queue

        self.channel.queue_bind(exchange='broadcast', queue=queue_name)

        def callback(ch, method, properties, body):
            print(" R[x] Received %r" % body)
        
        self.channel.basic_consume(
            queue=queue_name, on_message_callback=callback)
        
        self.channel.start_consuming()

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

    def JoinChat(self, user):
        client_producer = user
        #client_consumer = dest_user
        
        print("S[{}] {}".format(client_producer, msg))

        self.channel.basic_publish(
            exchange = 'user_channel',
            routing_key ='user_channel_route',
            body = client_producer,
            properties = pika.BasicProperties(
                delivery_mode=2, #2 hace que el mensaje sea persistente
            ))

        #Esperamos respuesta del server
        def callback(ch, method, properties, body):
            print(" R[x] Received %r" % body)
            if (body=="Ok"):
                return(True)
            return(False)
        #Declaramos exchange para control de usuarios
        self.channel.exchange_declare(exchange='user_channel', exchange_type='')

        #Declaramos la cola denuevo (buena practica)
        self.channel.queue_declare(queue=self.username, durable=True)

        #Declaramos a que cola va a enviar el mensaje el exchange
        self.channel.queue_bind(exchange='user_channel', queue=self.username)
        
        #El cliente obtiene el mensaje de la cola de mensajes
        response = self.channel.basic_consume(
            queue=self.username, on_message_callback=callback, auto_ack=True)

        self.channel.start_consuming()
        print(" [x] Sent 'Hello World!'")
        return(response)
        

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

    while True:
        print("Elija una opción")
        print("----------------------------")
        print("1) Enviar mensaje")
        print("2) Recibir mensajes")
        print("3) Mostrar lista de usuarios")
        print("4) Mostrar todos mis mensajes enviados")
        print("5) Salir del chat")
        opt = input("Su opción: ")

        if opt == '2':
            msg = input("Escriba su mensaje: ")
            c.send(msg)
        
        elif opt == '3':
            print("???")
            c.get_users()

        elif opt == '4':
            c.get_user_messages()

        elif opt == '5':
            c.disconnect()

    
    #c.get_users()
    #c.JoinChat()
    #client = Client()
    #client.send("hola")
    #run()