# -*- coding: utf-8 -*-
# pylint: disable=C0111,C0103,R0205

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

tickers = {
    'MXSE.EQBR.LKOH': (1933, 1940),
    'MXSE.EQBR.MSNG': (1.35, 1.45),
    'MXSE.EQBR.SBER': (90, 92),
    'MXSE.EQNE.GAZP': (156, 162),
    'MXSE.EQNE.PLZL': (1025, 1040),
    'MXSE.EQNL.VTBR': (0.05, 0.06)
}


def getticker():
    return list(tickers.keys())[random.randrange(0, len(tickers) - 1)]


_COUNT_ = 10

for i in range(0, _COUNT_):
    ticker = getticker()
    msg = {
        'order.stop.create': {
            'data': {
                'params': {
                    'condition': {
                        'ticker': ticker
                    }
                }
            }
        }
    }


def connect_to_server():
    connection = pika.BlockingConnection(
        # pika.ConnectionParameters(host='172.16.0.11'))
        pika.ConnectionParameters(host='10.80.10.231'))
    channel = connection.channel()
    return connection, channel


"""mandatory (bool): If set to True, the message will be returned (using a basic.return method) if it cannot be routed to a queue. 
This is useful for ensuring that messages are not lost due to invalid routing keys or non-existent queues."""


def send_msg_by_routing_key(msg_body, routing_key, expiration):
    connection, channel = connect_to_server()
    channel.confirm_delivery()
    try:
        channel.basic_publish(
            exchange='exchange_topics_inform',
            routing_key=routing_key,
            body=json.dumps(msg_body),
            properties=pika.BasicProperties(content_type='application/json',
                                            expiration=expiration,
                                            # delivery_mode=2,// durable
                                            headers={'key1': 'value1', 'key2': 'value2'}),
            mandatory=True
        )
        LOGGER.info('Message was published')
        LOGGER.info('send ticker %s' % ticker)
    except pika.exceptions.UnroutableError:
        LOGGER.info('Message was returned')

    connection.close()


def main():
    send_msg_by_routing_key(msg, "inform.#.email.#", "5000")


if __name__ == '__main__':
    main()
