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
    """
    Clase Cliente que se conecta al chat mediante RabbitMQ.

    Permite el envío/recepción de mensajes y obtención de listas.
    """
    def __init__(self):
        # Conexión con RabbitMQ. Se agrega un tiempo de espera para evitar que el cliente inicie antes
        # que el servidor de RabbitMQ.
        print("Iniciando conexión con RabbitMQ, por favor espere...")
        time.sleep(5)

        self.client_uuid = uuid.uuid4()
        self.username = ""
        self.is_logged = False

        # Conexión y channel mediante pika.
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq', heartbeat=0))
        self.channel = self.connection.channel()

    def _get_msgs(self):
        """
        Un método para la recepción de mensajes por parte de otros clientes/usuarios.

        Permite monitorear constantemente sin alterar la interacción del usuario mediante un thread que
        ejecuta el método paralelamente. 
        Se abre una nueva conexión y canal ya que RabbitMQ no soporta compartir canal entre threads.
        """
        # Conexión y channel mediante pika. 
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq', heartbeat=0))
        channel = connection.channel()

        # Declaración del exchange para recibir mensajes de otros usuarios mediante el productor.
        channel.exchange_declare(exchange='broadcast', exchange_type='fanout')

        # Declaración de cola exclusiva del cliente.
        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue

        # Enlace entre cola y exchange declarado previamente.
        channel.queue_bind(exchange='broadcast', queue=queue_name)

        def callback(ch, method, properties, body):
            """
            Una función que se ejecuta ante la llegada de un nuevo mensaje a la cola.
            
            Imprime en consola los mensajes enviados al Chat por otros clientes que y re-enviados
            por el productor.
            """
            message_received_string = body.decode("utf-8")
            message_received = json.loads(message_received_string)

            user = message_received["username"]
            text = message_received["message"]
            timestamp = message_received["timestamp"]
            dt_object = datetime.fromtimestamp(timestamp)
            date_time = dt_object.strftime("%m/%d/%Y, %H:%M:%S")

            print("[{} - {}]: {}".format(date_time, user, text))
        
        # Declaración de la cola a consumir.
        channel.basic_consume(
            queue=queue_name, on_message_callback=callback, auto_ack=True,
            consumer_tag=self.username)
        
        # Comenzar a consumir.
        channel.start_consuming()
        
    def get_msgs(self):
        """Un metodo que ejecuta el thread para la recepción de mensajes de usuarios."""
        threading.Thread(target=self._get_msgs, daemon=True).start()

    def _get_direct_messages(self):
        """
        Un método para la obtención y respuesta de mensajes a la cola exclusiva del usuario.

        Permite al cliente actuar en base a la variedad de mensajes que el productor puede agregar
        a la cola. No incluye los mensajes de otros usuarios. 
        """
        # Nueva conexión y channel para el thread.
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq', heartbeat=0))
        channel = connection.channel()

        # Declaración de una cola exclusiva para la recepción de mensajes directos del servidor.
        result = channel.queue_declare(queue=str(self.client_uuid), exclusive=True)
        queue_name = result.method.queue
        
        # Enlace de la cola con el exchange del productor para ruteos de mensajes.
        channel.queue_bind(exchange='user_channel', queue=queue_name)

        def callback(ch, method, properties, body):
            """
            Una función que se ejecuta ante la llegada de nuevos mensajes a la cola exclusiva.

            Permite al cliente actuar según el tipo de mensaje enviado. Incluye comandos por parte
            del usuario.
            """
            server_response = body.decode("utf-8")
            server_response_json = json.loads(server_response)    
            response_type = server_response_json["type"]            
            response = server_response_json["response"]

            # Si es un mensaje de confirmación de login
            if response_type == "login":
                
                if response == "ok":
                    self.is_logged = True
                    print("Inicio correcto. ¡Comience a chatear!")

                else:
                    print("Nombre de usuario ocupado\n")
                
                # Liberación del lock. Permite al objeto asignar al usuario y loguear.
                self.done_checking.set()

            # Si es un mensaje con la lista de mensajes enviados por el cliente.
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

            # Si es un mensaje con la lista de usuarios conectados al chat.
            elif response_type == "users_list":
                print("\n\n-----------------------------")
                print("Lista de usuarios")
                print("-----------------------------")
                for user in response:
                    print(user)
                print("")
            else:
                print("Problemas con el servidor")

        # Declaración de la cola a consumir.
        channel.basic_consume(
            queue=queue_name, on_message_callback=callback, auto_ack=True)

        # Comenzar a consumir
        channel.start_consuming()

    def get_direct_messages(self):
        """ Un método que ejecuta el thread para recepción de mensajes de la cola exclusiva"""
        threading.Thread(target=self._get_direct_messages, daemon=True).start()

    def send(self, message, option):
        """
        Un método para enviar (o dejar) mensajes en la cola del servidor.

        Pueden enviar multiples tipos de mensajes. Desde logueo hasta desconexión.
        """
        now = datetime.now()
        timestamp = datetime.timestamp(now)

        if message != '':

            # Si es un mensaje de logueo, se envían las credenciales.
            if option == "login":
                credentials = message

                message = {
                    'id': str(uuid.uuid4()),
                    'type': "login",
                    'username': credentials,
                    'client_uuid': str(self.client_uuid),
                    'timestamp': timestamp
                }

            # Si es un mensaje con texto, se envía el texto para ser transmitido por el productor.
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

            # Si es un mensaje de solicitud de usuarios.
            elif option == "users_list":
                message = {
                    'id': str(uuid.uuid4()),
                    'type': "users_list",
                    'username': self.username,
                    'client_uuid': str(self.client_uuid),
                    'timestamp': timestamp
                }

            # Si es un mensaje de solicitud de mensajes enviados por el cliente.
            elif option == "user_messages":
                message = {
                    'id': str(uuid.uuid4()),
                    'type': "user_messages_list",
                    'username': self.username,
                    'client_uuid': str(self.client_uuid),
                    'timestamp': timestamp
                }

            # Si es una solicitud de desconexión del chat.
            elif option == "disconnect":
                message = {
                    'id': str(uuid.uuid4()),
                    'type': "disconnect",
                    'username': self.username,
                    'client_uuid': str(self.client_uuid),
                    'timestamp': timestamp
                }

            # Parseo de JSON a string
            body_message = json.dumps(message)

            # Envío de mensaje a la cola del servidor.
            self.channel.basic_publish(
                exchange='',
                routing_key='server_pending_messages',
                body=body_message,
                properties = pika.BasicProperties(content_type='text/plain', delivery_mode=2)
            )

    def connect(self):
        """Un método para conectar al cliente al chat y asignar un nombre de usuario."""
        # Se define un evento para bloquear un thread.
        self.done_checking = threading.Event()

        while not self.is_logged:
            username = input("Ingrese nombre de usuario: ")

            if (username == "") or ('' in username == True):
                print("No puede ingresar campos vacíos")

            else:
                # Consulta al servidor si se puede usar el nombre de usuario.
                self.send(username, "login")
                # Se bloquea el while hasta obtener un mensaje del servidor.
                self.done_checking.wait()
                # Se libera nuevamente el evento.
                self.done_checking.clear()

        self.username = username

    def disconnect(self):
        """ Un método para desconectar al cliente del chat, liberar su usuario y borrar sus mensajes."""
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