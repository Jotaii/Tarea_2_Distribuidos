from concurrent import futures
import logging

import pika
import os
import time

import sys

time.sleep(5)
chats = []
users = []

connection = pika.BlockingConnection(
    pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()

#channel.queue_declare(queue="server_receive_user", durable=True)
channel.queue_declare(queue="server_pending_messages", durable=True)

channel.exchange_declare(exchange='user_channel', exchange_type='direct')
channel.exchange_declare(exchange='broadcast', exchange_type='fanout')

def on_request(ch, method, props, body):
    #response = "[USER ID]: {}".format(body)
    response = "ok"
    channel.basic_publish(
        exchange='broadcast', 
        routing_key='', 
        body=response
    )

    f = open("log.txt", "a+")
    f.write(str(body))
    f.close()

    channel.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='server_pending_messages', on_message_callback=on_request)

channel.start_consuming()