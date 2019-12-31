from __future__ import print_function
import logging
import socket
import threading

import pika


class Client:

    def __init__(self):

        self.connection = pika.BlockingConnection(pika.ConnectionParameters('server:50051'))
        self.channel = self.connection.channel()

        exit = False
        while exit == False:
            username = input("Ingrese nombre de usuario: ")
            self.user_id = username
            
            #Falta verificar aca cual es la nueva respuesta en rabbitmq sin stub.join
            #JoinChat aun no esta definida
            response = self.JoinChat(username)

            if response.opt:
                print("Logueado correctamente")
                self.username = username
                exit = True

            else:
                print("Nombre de usuario no disponible. Ingrese otro nombre de usuario")
        
        self.channel.queue_declare(queue=self.user_id, durable=True)
        self.channel.exchange_declare(exchange='broadcast',
                         exchange_type='fanout')
        threading.Thread(target=self.get_msgs, daemon=True).start()

    
    def get_msgs(self):

        def callback(ch, method, properties, body):
            print(" R[x] Received %r" % body)
        #Declaramos la cola denuevo (buena practica)
        self.channel.queue_declare(queue=self.user_id, durable=True)

        self.channel.queue_bind(exchange='broadcast', queue=self.user_id)

        self.channel.basic_consume(queue=self.user_id,
                            auto_ack=True,
                            on_message_callback=callback)

        print(' [*] Waiting for messages. To exit press CTRL+C')
        self.channel.start_consuming()

    def send(self, dest_user, msg):
        if msg != '':
            client_producer = self.username
            #client_consumer = dest_user
            
            print("S[{}] {}".format(client_producer, msg))

            self.channel.basic_publish(exchange='broadcast',
                                  routing_key='',
                                  body=msg,
                                  properties= pika.BasicProperties(
                                      delivery_mode=2,
                                  ))
            print(" [x] Sent 'Hello World!'")


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
        self.channel.queue_declare(queue=self.user_id, durable=True)

        self.channel.queue_bind(exchange='broadcast', queue=self.user_id)

        

        print("Lista de mensajes enviados: ")
        print("-----------------------------")
        self.channel.basic_consume(queue=self.user_id,
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
            c.send(c.username, msg)

        
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