"""AMQP consumer for testing cat2queue."""

import pprint

import pika

EXCHANGE = 'test'

CONNECTION = pika.BlockingConnection()

CHANNEL = CONNECTION.channel()

CHANNEL.exchange_declare(exchange=EXCHANGE, type='topic')

QUEUE_NAME = CHANNEL.queue_declare(exclusive=True).method.queue

CHANNEL.queue_bind(exchange=EXCHANGE, queue=QUEUE_NAME, routing_key='#')
 
def callback(*args):
    """Pretty print the args."""
    pprint.pprint(args)

CHANNEL.basic_consume(callback, queue=QUEUE_NAME, no_ack=True)

CHANNEL.start_consuming()
