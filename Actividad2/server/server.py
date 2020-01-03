from concurrent import futures
from datetime import datetime
import logging

import pika
import os
import time
import json
import sys
import uuid


time.sleep(5)
chats = {}
users = {}
logged_users = []

connection = pika.BlockingConnection(
    pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()

#channel.queue_declare(queue="server_receive_user", durable=True)
channel.queue_declare(queue="server_pending_messages", durable=True)

channel.exchange_declare(exchange='user_channel', exchange_type='direct')
channel.exchange_declare(exchange='broadcast', exchange_type='fanout')

def on_request(ch, method, props, body):
    user_message_string = body.decode("utf-8")
    user_message_json = json.loads(user_message_string)
    now = datetime.now()
    
    request_type = user_message_json["type"]
    client_uuid = str(user_message_json["client_uuid"])

    timestamp = datetime.timestamp(now)

    # Registro de usuario único en el server.
    if request_type == "register":
        username = user_message_json["username"]
        password = user_message_json["password"]
        response = "nope"

        if username not in users.keys():
            users[username] = password
            response = "ok"
            logged_users.append(username)

        response_message = {
            'id': str(uuid.uuid4()),
            'type': "register",
            'response': response,
            'uuid': client_uuid,
            'timestamp': timestamp
        }

        body_response = json.dumps(response_message)

        channel.basic_publish(
            exchange='user_channel', 
            routing_key=client_uuid, 
            body=body_response)

    # Inicio de sesión.
    elif request_type == "login":
        username = user_message_json["username"]
        password = user_message_json["password"]
        response = "nope"

        # Usuario existe y no está logueado
        if username in users.keys():
            # Contraseñas coinciden
            if users[username] == password:
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
        username = user_message_json["username"]

        if username not in chats:
            chats[username] = [user_message_string]

        else:
            chats[username].append(user_message_string)

        channel.basic_publish(
            exchange='broadcast', 
            routing_key='', 
            body=body
        )
        
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
        username = user_message_json["username"]

        response_message = {
            'id': str(uuid.uuid4()),
            'type': "user_messages",
            'response': chats[username]
        }

        body_response = json.dumps(response_message)

        channel.basic_publish(
            exchange='user_channel', 
            routing_key=client_uuid, 
            body=body_response)

    channel.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='server_pending_messages', on_message_callback=on_request)

channel.start_consuming()