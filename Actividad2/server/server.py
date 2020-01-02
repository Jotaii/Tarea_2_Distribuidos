from concurrent import futures
import logging

import pika
import os
import time


class Chat():

    def __init__(self):
        self.chats = []
        self.users = []

        time.sleep(10)
        #amqp_url = os.environ['AMQP_URL']
        #parameters = pika.URLParameters(amqp_url)
        #self.connection = pika.SelectConnection(parameters)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue="server_receive_user", durable=True)
        self.channel.queue_declare(queue="server_pending_messages", durable=True)

        self.channel.exchange_declare(exchange='broadcast', exchange_type='fanout')
        self.channel.exchange_declare(exchange='user_channel', exchange_type='direct')


    def SendMsg(self):

        #Ver como hacer el log
        f = open("log.txt", "a")
        f.write("[" + request.client_id + "]: " + request.message + "\n")
        f.close()

        def on_request(ch, method, props, body):
            
            response = "[USER ID]: {}".format(body)

            self.channel.basic_publish(exchange='broadcast',
                            routing_key="",
                            body=response)

            self.channel.basic_ack(delivery_tag=method.delivery_tag)

        #Recibe el elemento de la cola y le hace broadcast
        self.channel.basic_consume(queue='server_pending_mesagges', on_message_callback=on_request)
        
    def Start(self):
        self.channel.start_consuming()

def serve():
    #Hacer correr el servidor
    server = Chat()
    server.Start()

if __name__ == '__main__':
    logging.basicConfig()
    serve()
