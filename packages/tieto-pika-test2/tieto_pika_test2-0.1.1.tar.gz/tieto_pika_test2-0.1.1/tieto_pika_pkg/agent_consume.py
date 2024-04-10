"""Basic message consumer example"""
import functools
import logging
import pika

from tieto_pika.tieto_pika_pkg import exceptions

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


def on_message(chan, method_frame, header_frame, body, userdata=None, handler=None):
    try:
        LOGGER.info('Delivery properties: %s, message metadata: %s', method_frame, header_frame)
        LOGGER.info('Userdata: %s, message body: %s', userdata, body)
        """"start handle message"""
        handler
        chan.basic_ack(delivery_tag=method_frame.delivery_tag)
    except exceptions.MessageHandleError:
        print("MessageHandleError.")
        LOGGER.info('DeliveryTag: %s', method_frame.delivery_tag)
        chan.basic_nack(
            delivery_tag=method_frame.delivery_tag,  # 交付这标记，和basic_ack一样
            multiple=False,  # Flase表示拒绝单个消息，为True表示拒绝多个消息
            requeue=False)  # True表示拒绝了消息后重新放回队列，False表示丢弃消息


def receive_message(handler):
    """Main method."""
    credentials = pika.PlainCredentials('guest', 'guest')
    parameters = pika.ConnectionParameters('10.80.10.231', credentials=credentials)
    connection = pika.BlockingConnection(parameters)

    channel = connection.channel()

    on_message_callback = functools.partial(
        on_message, userdata='on_message_userdata', handler=handler)
    channel.basic_consume('queue_inform_email', on_message_callback)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()

    connection.close()


if __name__ == '__main__':
    receive_message()
