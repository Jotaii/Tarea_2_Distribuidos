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
chats = []
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

    request_type = user_message_json["type"]
    username = user_message_json["username"]

    if request_type == "register":
        password = user_message_json["password"]
        client_uuid = str(user_message_json["uuid"])

        if username not in users.keys():
            users[username] = password
   
            response_message = {
                'type': "register-confirm",
                'response': "ok",
                'uuid': client_uuid
            }

            channel.basic_publish(
                exchange='user_channel', 
                routing_key=client_uuid, 
                body="ok")

            logged_users.append(username)

        else:
            channel.basic_publish(
                exchange='user_channel', 
                routing_key=client_uuid, 
                body="not ok")

    elif request_type == "login":
        password = user_message_json["password"]
        client_uuid = str(user_message_json["uuid"])

        if username not in users.keys() or username in logged_users:
            response = "not ok"

        else:

            if users[username] == password:
                response = "ok"
                logged_users.append(username)
            
            else:
                response = "not ok"

        now = datetime.now()
        timestamp = datetime.timestamp(now)

        server_response = {
            'type': "login_confirm",
            'id': str(uuid.uuid4()),
            'response': response,
            'timestamp': timestamp
        }

        body_response = json.dumps(server_response)

        channel.basic_publish(
            exchange='user_channel', 
            routing_key=client_uuid, 
            body=body_response)

    elif request_type == "message":
        channel.basic_publish(
            exchange='broadcast', 
            routing_key='', 
            body=body
        )

        """
        f = open("log.txt", "a+")
        f.write(str(body))
        f.close()
        """
        
    elif request_type == "users_list":
        pass

    elif request_type == "user_messages_list":
        pass

    else:
        pass

    channel.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='server_pending_messages', on_message_callback=on_request)

channel.start_consuming()