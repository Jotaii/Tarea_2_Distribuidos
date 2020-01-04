from concurrent import futures
from datetime import datetime
import logging

import pika
import os
import time
import json
import sys
import uuid

# Espera a que RabbitMQ inicie.
time.sleep(10)

# Estructuras de datos para almacenamiento de mensajes y usuarios.
chats = {}
logged_users = []

# Conexión y creación de channel a RabbitMQ mediante pika.
connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()

# Declaración de cola para recibir mensajes por parte de los clientes.
channel.queue_declare(queue="server_pending_messages", durable=True)

# Declaración de exchange para ruteo de mensajes a colas de clientes (exclusivo para cada uno).
channel.exchange_declare(exchange='user_channel', exchange_type='direct')

# Declaración de exchange para transmisión de un mensaje a todos los usuarios.
channel.exchange_declare(exchange='broadcast', exchange_type='fanout')

def on_request(ch, method, props, body):
    """
    Una función que se ejecuta ante la llegada de un nuevo mensaje a la cola del servidor por parte 
    de un cliente.
    """
    # Parseo de mensaje a JSON
    user_message_string = body.decode("utf-8")
    user_message_json = json.loads(user_message_string)
    now = datetime.now()
    
    # Obtención de atributos.
    request_type = user_message_json["type"]
    username = user_message_json["username"]
    client_uuid = str(user_message_json["client_uuid"])

    # Fecha y hora del server.
    timestamp = datetime.timestamp(now)

    # Inicio de sesión.
    if request_type == "login":
        response = "nope"

        if username not in logged_users:
            response = "ok"
            logged_users.append(username)                 

        response_message = {
            'id': str(uuid.uuid4()),
            'type': "login",
            'response': response,
            'uuid': client_uuid,
            'timestamp': timestamp
        }

        body_response = json.dumps(response_message)

        channel.basic_publish(
            exchange='user_channel', 
            routing_key=client_uuid, 
            body=body_response)
    
    # Broadcast de mensaje de usuario.
    elif request_type == "message":
        # Reemplazo de timestamp para mantener consistencia de hora en el chat.
        sender_timestamp = user_message_json["timestamp"]
        user_message_json["timestamp"] = timestamp

        if username not in chats:
            chats[username] = [user_message_string]

        else:
            chats[username].append(user_message_string)

        body_response = json.dumps(user_message_json)

        channel.basic_publish(
            exchange='broadcast', 
            routing_key='', 
            body=body_response
        )

        # Registro en log.txt.
        f = open("log.txt", "a")
        
        f.write("Registro de mensaje: \n")
        dt_object = datetime.fromtimestamp(user_message_json["timestamp"])
        date_time = dt_object.strftime("%m/%d/%Y, %H:%M:%S")
        f.write("ID Mensaje: " + user_message_json["id"] + "\n")
        f.write("Usuario: " + username + "\n") 
        f.write("ID Cliente: " + client_uuid + "\n")
        f.write("Mensaje: " + user_message_json["message"] + "\n")
        dt_object = datetime.fromtimestamp(sender_timestamp)
        date_time = dt_object.strftime("%m/%d/%Y, %H:%M:%S")
        f.write("Fecha recepcion en server: " + date_time+"\n")
        f.write("Fecha de envio en cliente: " + date_time + "\n\n")
        """
        dt_object = datetime.fromtimestamp(user_message_json["timestamp"])
        date_time = dt_object.strftime("%m/%d/%Y, %H:%M:%S")
        text = user_message_json["message"]
        f.write("[{} - {}]: {}\n".format(date_time, username, text))
        """
        f.close()
        
    # Envío de lista de usuarios conectados.
    elif request_type == "users_list":
        response_message = {
            'id': str(uuid.uuid4()),
            'type': "users_list",
            'response': logged_users
        }

        body_response = json.dumps(response_message)
        
        channel.basic_publish(
            exchange='user_channel', 
            routing_key=client_uuid, 
            body=body_response)

    # Envío de lista de mensajes enviados por el usuario que lo solicita.
    elif request_type == "user_messages_list":
        
        if username in chats:
            user_messages = chats[username]

        else:
            user_messages = []


        response_message = {
            'id': str(uuid.uuid4()),
            'type': "user_messages",
            'response': user_messages
        }

        body_response = json.dumps(response_message)

        channel.basic_publish(
            exchange='user_channel', 
            routing_key=client_uuid, 
            body=body_response)

    # Usuario se desconecta. Se elimina a usuario de la lista de conectados y sus mensajes (sus copias están en log.txt).
    elif request_type == "disconnect":
        username = user_message_json["username"]
        logged_users.remove(username)
        chats.pop(username, None)

    channel.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='server_pending_messages', on_message_callback=on_request)

channel.start_consuming()