#!/usr/bin/env python
"""Read lines from stdin and send them to AMQP message queues if they match
regular expressions.

See https://github.com/mmb/cat2queue for more information.
"""

import argparse
import json
import re
import sys
import urlparse

import pika

class AmqpDest:
    """An AMQP destination (URI, exchange and routing keys)."""

    def __init__(self, uri, exchange, routing_keys):
        self.exchange = exchange
        self.routing_keys = routing_keys

        parsed = urlparse.urlparse(uri)
        self.username = parsed.username
        self.password = parsed.password
        self.hostname = parsed.hostname
        self.port = parsed.port or pika.spec.PORT
        self.vhost = parsed.path

        self.connection = None
        self.channel = None

    def credentials(self):
        """Build pika.PlainCredentials for this destination.

        Return None if no username and password have been provided.
        """
        if self.username and self.password:
            return pika.PlainCredentials(self.username, self.password)

    def connection_params(self):
        """Build pika.ConnectionParameters for this destination."""
        return pika.ConnectionParameters(
            credentials=self.credentials(),
            host=self.hostname,
            port=self.port,
            virtual_host=self.vhost)

    def check_connection(self):
        """Connect to AMQP if not connected."""
        if not self.connection or not self.connection.is_open:
            self.connection = pika.BlockingConnection(self.connection_params())
            self.channel = self.connection.channel()

            self.channel.exchange_declare(
                exchange=self.exchange,
                type='topic')

    def publish(self, routing_keys, body):
        """Publish a message to this destination."""
        self.check_connection()

        self.channel.basic_publish(
            exchange=self.exchange,
            routing_key='.'.join(self.routing_keys + routing_keys),
            body=body)

if __name__ == '__main__':
    ARG_PARSER = argparse.ArgumentParser(description=__doc__)

    ARG_PARSER.add_argument(
        '--config', '-c', required=True, help='path to JSON config file')

    ARGS = ARG_PARSER.parse_args()

    with open(ARGS.config) as config_handle:
        CONFIG = json.load(config_handle)

        ROUTES = []

        for route in CONFIG['routes']:
            regex = re.compile(route['regex'])

            dests = [
                AmqpDest(
                    dest['server'].encode('ascii'),
                    dest['exchange'].encode('ascii'),
                    dest['routing_keys'])
                for dest in route['dests'] ]

            ROUTES.append((regex, dests))

        while True:
            LINE = sys.stdin.readline()[:-1]

            for regex, dests in ROUTES:
                match = regex.search(LINE)

                if match:
                    for dest in dests:
                        dest.publish(list(match.groups()), LINE)
