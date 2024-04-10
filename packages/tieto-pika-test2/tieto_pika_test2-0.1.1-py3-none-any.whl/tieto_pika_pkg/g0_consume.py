# -*- coding: utf-8 -*-
# pylint: disable=C0111,C0103,R0205
import functools
import json
import random
import pika
import logging
from pika import exceptions
from pika.exchange_type import ExchangeType

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='172.16.0.11'))
main_channel = connection.channel()


def on_message(chan, method_frame, header_frame, body, userdata=None):
    LOGGER.info("dead letter")
    LOGGER.info('Userdata: %s, message body: %s', userdata, body)


def main():
    """Main method."""
    credentials = pika.PlainCredentials('guest', 'guest')
    parameters = pika.ConnectionParameters('10.80.10.231', credentials=credentials)
    connection = pika.BlockingConnection(parameters)

    channel = connection.channel()

    on_message_callback = functools.partial(
        on_message, userdata='on_message_userdata')
    channel.basic_consume('deadQueue', on_message_callback, auto_ack=True)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()

    connection.close()


if __name__ == '__main__':
    main()
